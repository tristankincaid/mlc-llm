"""Common utilities for quantization"""
from typing import List, Optional

from tvm import te, tir


def convert_uint_to_float(  # pylint: disable=too-many-arguments
    weight: te.Tensor,
    bits: int,
    num_elem_per_storage: int,
    storage_dtype: str,
    model_dtype: str,
    out_shape: Optional[List[tir.PrimExpr]] = None,
) -> te.Tensor:
    """Convert a quantized uint weight to an unquantized float weight."""
    tir_bin_mask = tir.const((1 << bits) - 1, storage_dtype)
    return te.compute(
        shape=[weight.shape[0], weight.shape[1] * num_elem_per_storage]
        if out_shape is None
        else out_shape,
        fcompute=lambda i, j: tir.bitwise_and(
            tir.shift_right(
                weight[i, j // num_elem_per_storage],
                ((j % num_elem_per_storage) * bits).astype(storage_dtype),
            ),
            tir_bin_mask,
        ).astype(model_dtype),
    )
