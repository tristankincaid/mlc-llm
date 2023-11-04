"""This file specifies how MLC's Llama parameters are quantized using group quantization
or other formats."""
from typing import Tuple

from tvm.relax.frontend import nn

from ..loader import QuantizeMapping
from ..quantization import GroupQuantize
from .llama_model import LlamaConfig, LlamaForCasualLM


def group_quant(
    model_config: LlamaConfig,
    quantization: GroupQuantize,
) -> Tuple[nn.Module, QuantizeMapping]:
    """Quantize a Llama2 model using group quantization."""
    model: nn.Module = LlamaForCasualLM(model_config)
    quant_map = QuantizeMapping({}, {})
    model = quantization.quantize_model(
        model,
        quant_map,
        "",
    )
    return model, quant_map
