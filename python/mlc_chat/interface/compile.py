"""Python entrypoint of compilation."""
import dataclasses
from io import StringIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from tvm import IRModule, relax, tir
from tvm.ir.transform import Pass
from tvm.relax.frontend import nn
from tvm.target import Target

from mlc_chat import compiler_pass as _
from mlc_chat import operator as op_ext
from mlc_chat.model import Model
from mlc_chat.quantization import Quantization
from mlc_chat.support import argparse, logging
from mlc_chat.support.config import ConfigBase
from mlc_chat.support.style import bold

from .flags_model_config_override import ModelConfigOverride

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class OptimizationFlags:
    """Optimization flags"""

    flashinfer: bool = False
    cublas_gemm: bool = False
    cudagraph: bool = False

    def __repr__(self) -> str:
        out = StringIO()
        print(f"flashinfer={int(self.flashinfer)}", file=out, end="")
        print(f";cublas_gemm={int(self.cublas_gemm)}", file=out, end="")
        print(f";cudagraph={int(self.cudagraph)}", file=out, end="")
        return out.getvalue().rstrip()

    @staticmethod
    def from_str(source: str) -> "OptimizationFlags":
        """Parse optimization flags from a string."""

        if source in OPT_FLAG_PRESET:
            return OPT_FLAG_PRESET[source]

        def boolean(value: str) -> bool:
            if value == "0":
                return False
            if value == "1":
                return True
            raise ValueError(f"Invalid boolean value: {value}")

        parser = argparse.ArgumentParser(description="optimization flags")
        parser.add_argument("--flashinfer", type=boolean, default=True)
        parser.add_argument("--cublas_gemm", type=boolean, default=False)
        parser.add_argument("--cudagraph", type=boolean, default=False)
        results = parser.parse_args([f"--{i}" for i in source.split(";") if i])
        return OptimizationFlags(
            flashinfer=results.flashinfer,
            cublas_gemm=results.cublas_gemm,
            cudagraph=results.cudagraph,
        )

    def update(self, target: Target) -> None:
        """Update optimization flags based on additional information."""

        def _flashinfer(target) -> bool:
            from mlc_chat.support.auto_target import (  # pylint: disable=import-outside-toplevel
                detect_cuda_arch_list,
            )

            if not self.flashinfer:
                return False
            if target.kind.name != "cuda":
                return False
            arch_list = detect_cuda_arch_list(target)
            for arch in arch_list:
                if arch < 80:
                    logger.warning("flashinfer is not supported on CUDA arch < 80")
                    return False
            return True

        self.flashinfer = _flashinfer(target)


@dataclasses.dataclass
class CompileArgs:  # pylint: disable=too-many-instance-attributes
    """Arguments to MLC LLM's compiler."""

    config: Path
    quantization: Quantization
    model: Model
    target: Target
    opt: OptimizationFlags
    build_func: Callable[[IRModule, "CompileArgs", Pass], None]
    system_lib_prefix: str
    output: Path
    overrides: ModelConfigOverride
    debug_dump: Optional[Path]

    def __post_init__(self) -> None:
        self.opt.update(self.target)

    def display(self) -> None:
        """Display the arguments to stdout."""
        out = StringIO()
        print(f"{bold('Compiling with arguments:')}", file=out)
        print(f"  {bold('--config'):<25} {self.config}", file=out)
        print(f"  {bold('--quantization'):<25} {self.quantization}", file=out)
        print(f"  {bold('--model-type'):<25} {self.model.name}", file=out)
        print(f"  {bold('--target'):<25} {self.target.export()}", file=out)
        print(f"  {bold('--opt'):<25} {self.opt}", file=out)
        print(f"  {bold('--system-lib-prefix'):<25} \"{self.system_lib_prefix}\"", file=out)
        print(f"  {bold('--output'):<25} {self.output}", file=out)
        print(f"  {bold('--overrides'):<25} {self.overrides}", file=out)
        # As it's debug only, no need to display
        # print(f"  {bold('--debug-dump'):<25} {self.debug_dump}", file=out)
        print(out.getvalue().rstrip())


def _apply_preproc_to_params(
    named_params: List[Tuple[str, nn.Parameter]],
    model_config,
) -> Dict[str, tir.PrimFunc]:
    extra_tirs: Dict[str, tir.PrimFunc] = {}
    for _, param in named_params:
        preprocs = param.attrs.get("preprocs", [])
        shard_strategy = param.attrs.get("shard_strategy", None)
        if shard_strategy is not None and model_config.tensor_parallel_shards > 1:
            preprocs.append(
                shard_strategy.gen_shard_info(
                    shards=model_config.tensor_parallel_shards,
                    weight=param,
                )
            )
            if shard_strategy.name not in extra_tirs:
                extra_tirs[shard_strategy.name] = shard_strategy.gen_tir(
                    shards=model_config.tensor_parallel_shards,
                    weight=param,
                )
        param.attrs["preprocs"] = preprocs
    return extra_tirs


def _compile(args: CompileArgs, model_config: ConfigBase):
    def _get_variable_bounds(model_config) -> Dict[str, int]:
        if hasattr(model_config, "sliding_window_size"):
            return {
                "seq_len": model_config.prefill_chunk_size,
                "rolling_cache_len": model_config.sliding_window_size,
                "kv_seq_len": model_config.sliding_window_size + model_config.prefill_chunk_size,
            }
        return {
            "seq_len": model_config.prefill_chunk_size,
            "total_seq_len": model_config.context_window_size,
        }

    def _get_param_metadata(name: str, param: nn.Parameter) -> Dict[str, Any]:
        return {
            "name": name,
            "shape": list(param.shape),
            "dtype": param.dtype,
            "preprocs": param.attrs["preprocs"],
        }

    args.overrides.apply(model_config)
    with args.target:
        op_ext.enable(
            target=args.target,
            flashinfer=args.opt.flashinfer,
        )
        # Step 1. Create the quantized model
        logger.info("Creating model from: %s", args.config)
        model, _ = args.model.quantize[args.quantization.kind](model_config, args.quantization)
        # Step 2. Exporting the model to TVM Unity
        logger.info("Exporting the model to TVM Unity compiler")
        mod, named_params, ext_mods = model.export_tvm(
            spec=model.get_default_spec(),  # type: ignore
            allow_extern=True,
        )
        # Step 3. Running relax compilation pipeline
        logger.info("Running optimizations using TVM Unity")
        additional_tirs = _apply_preproc_to_params(named_params, model_config)
        variable_bounds = _get_variable_bounds(model_config)
        metadata = {
            "model_type": args.model.name,
            "quantization": args.quantization.name,
            "context_window_size": model_config.context_window_size,  # type: ignore
            "prefill_chunk_size": model_config.prefill_chunk_size,  # type: ignore
            "sliding_window_size": getattr(model_config, "sliding_window_size", -1),
            "attention_sink_size": getattr(model_config, "attention_sink_size", -1),
            "tensor_parallel_shards": model_config.tensor_parallel_shards,  # type: ignore
        }
        logger.info("Registering metadata: %s", metadata)
        metadata["params"] = [_get_param_metadata(name, param) for name, param in named_params]
        args.build_func(
            mod,
            args,
            pipeline=relax.get_pipeline(  # type: ignore
                "mlc_llm",
                variable_bounds=variable_bounds,
                additional_tirs=additional_tirs,
                ext_mods=ext_mods,
                metadata=metadata,
                debug_dump=args.debug_dump,
            ),
        )
    logger.info("Generated: %s", bold(str(args.output)))


def compile(  # pylint: disable=too-many-arguments,redefined-builtin
    config: Dict[str, Any],
    quantization: Quantization,
    model_type: Model,
    target: Target,
    opt: OptimizationFlags,
    build_func: Callable[[IRModule, CompileArgs, Pass], None],
    system_lib_prefix: str,
    output: Path,
    overrides: ModelConfigOverride,
    debug_dump: Optional[Path] = None,
):
    """Compile a model given its configuration and quantization format to a specific target."""
    if "model_config" in config:
        model_config = model_type.config.from_dict({**config["model_config"], **config})
    else:
        model_config = model_type.config.from_dict(config)
    args = CompileArgs(
        model_config,
        quantization,
        model_type,
        target,
        opt,
        build_func,
        system_lib_prefix,
        output,
        overrides,
        debug_dump,
    )
    args.display()
    _compile(args, model_config)


OPT_FLAG_PRESET = {
    "O0": OptimizationFlags(
        flashinfer=False,
        cublas_gemm=False,
        cudagraph=False,
    ),
    "O1": OptimizationFlags(
        flashinfer=False,
        cublas_gemm=True,
        cudagraph=False,
    ),
    "O2": OptimizationFlags(
        flashinfer=False,
        cublas_gemm=True,
        cudagraph=False,
    ),
    "O3": OptimizationFlags(
        flashinfer=True,
        cublas_gemm=True,
        cudagraph=True,
    ),
}
