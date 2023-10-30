"""Python entrypoint of compilation."""
import dataclasses
from io import StringIO
from pathlib import Path
from typing import Callable

from tvm import IRModule, relax
from tvm.target import Target

from ..compiler.model import Model
from ..support.style import bold
from .flags_optimization import OptimizationFlags


@dataclasses.dataclass
class CompileArgs:  # pylint: disable=too-many-instance-attributes
    """Arguments to MLC LLM's compiler."""

    config: Path
    quantization: str
    model: Model
    target: Target
    opt: OptimizationFlags
    build_func: Callable[[IRModule, "CompileArgs"], None]
    prefix_symbols: str
    output: Path


def _echo_args(args: CompileArgs) -> None:
    out = StringIO()
    print(f"{bold('Compiling with arguments:')}", file=out)
    print(f"  {bold('--config'):<25} {args.config}", file=out)
    print(f"  {bold('--quantization'):<25} {args.quantization}", file=out)
    print(f"  {bold('--model-type'):<25} {args.model.name}", file=out)
    print(f"  {bold('--target'):<25} {args.target.export()}", file=out)
    print(f"  {bold('--opt'):<25} {args.opt}", file=out)
    print(f"  {bold('--output'):<25} {args.output}", file=out)
    print(out.getvalue().rstrip())


def _compile(args: CompileArgs):
    model_config = args.model.config.from_file(args.config)
    model = args.model.model(model_config)
    mod, named_params = model.export_tvm(
        spec=model.get_default_spec(),  # type: ignore
    )
    with args.target:
        mod = relax.get_pipeline("mlc_llm")(mod)
    mod.show(black_format=False)
    for name, param in named_params:
        print(f"{name}: {param.shape} {param.dtype}")


def compile(  # pylint: disable=too-many-arguments,redefined-builtin
    config: Path,
    quantization,
    model_type: Model,
    target: Target,
    opt: OptimizationFlags,
    build_func: Callable[[IRModule, CompileArgs], None],
    prefix_symbols: str,
    output: Path,
):
    """Compile a model given its configuration and quantization format to a specific target."""
    args = CompileArgs(
        config, quantization, model_type, target, opt, build_func, prefix_symbols, output
    )
    _echo_args(args)
    _compile(args)
