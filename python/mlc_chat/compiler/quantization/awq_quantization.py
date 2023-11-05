"""AWQ Quantization"""

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np
from tvm import DataType, DataTypeCode, te, tir
from tvm.relax.frontend import nn
from tvm.runtime import NDArray

from ..loader import QuantizeMapping


def _make_divisible(c, divisor):  # pylint: disable=invalid-name
    return (c + divisor - 1) // divisor


def _calculate_zeros_width(in_features, group_size=128, pack_num=8):
    if group_size >= 128:
        size_multiplier = 1
    elif group_size == 64:
        size_multiplier = 2
    elif group_size == 32:
        size_multiplier = 4
    else:
        raise NotImplementedError

    base_width = _make_divisible(in_features // group_size, pack_num)
    base_width = _make_divisible(base_width, size_multiplier) * size_multiplier
    return base_width


@dataclass
class AWQQuantize:  # pylint: disable=too-many-instance-attributes
    """Configuration for AWQ quantization"""

    name: str
    kind: str
    group_size: int
    quantize_dtype: str  # "int3", "int4", "int8"
    storage_dtype: str  # "uint32"
    model_dtype: str  # "float16", "float32"

    num_elem_per_storage: int = 0
    num_storage_per_group: int = 0
    max_int_value: int = 0

    prebuilt_quantize_func: Dict[str, Callable[[NDArray], NDArray]] = field(
        default_factory=lambda: {}
    )

    def __post_init__(self):
        assert self.kind == "awq"
        quantize_dtype = DataType(self.quantize_dtype)
        storage_dtype = DataType(self.storage_dtype)
        model_dtype = DataType(self.model_dtype)
        assert quantize_dtype.type_code == DataTypeCode.INT
        assert storage_dtype.type_code == DataTypeCode.UINT
        assert model_dtype.type_code == DataTypeCode.FLOAT
        if storage_dtype.bits < quantize_dtype.bits:
            raise ValueError("Storage unit should be greater or equal to quantized element")

        self.num_elem_per_storage = storage_dtype.bits // quantize_dtype.bits
        if self.group_size % self.num_elem_per_storage != 0:
            raise ValueError("Group size should be divisible by numbers of elements per storage")
        self.num_storage_per_group = self.group_size // self.num_elem_per_storage
        self.max_int_value = (2 ** (quantize_dtype.bits - 1)) - 1

    def quantize_model(
        self,
        model: nn.Module,
        quant_map: QuantizeMapping,
        name_prefix: str,
    ) -> nn.Module:
        """
        Quantize model with awq quantization.

        Parameters
        ----------
        model : nn.Module
            The non-quantized nn.Module.

        quant_map : QuantizeMapping
            The quantize mapping with name mapping and func mapping.

        name_prefix : str
            The name prefix for visited weight.

        Returns
        -------
        ret : nn.Module
            The quantized nn.Module.
        """

        class _Mutator(nn.Mutator):
            def __init__(self, config: AWQQuantize, quant_map: QuantizeMapping) -> None:
                super().__init__()
                self.config = config
                self.quant_map = quant_map

            def visit_module(self, name: str, node: nn.Module) -> Any:
                """
                The visiting method for awq quantization of nn.Module nodes.

                Parameters
                ----------
                name : str
                    The name of the current node

                node : nn.Module
                    The current node of nn.Module to mutate.

                Returns
                -------
                ret_node : Any
                    The new node to replace current node.
                """

                if isinstance(node, nn.Linear) and name != "lm_head":
                    return AWQQuantizeLinear.from_linear(node, self.config)
                if isinstance(node, nn.MultiLinear):
                    return AWQQuantizeMultiLinear.from_multilinear(node, self.config)
                return self.visit(name, node)

        model.to(dtype=self.model_dtype)
        mutator = _Mutator(self, quant_map)
        model = mutator.visit(name_prefix, model)
        return model

    def _dequantize(
        self,
        weight: te.Tensor,
        zeros: te.Tensor,
        scale: te.Tensor,
        out_shape: Optional[List[tir.PrimExpr]] = None,
    ):
        tir_bin_mask = tir.const((1 << DataType(self.quantize_dtype).bits) - 1, self.storage_dtype)
        return te.compute(
            shape=[weight.shape[0], weight.shape[1] * self.num_elem_per_storage]
            if out_shape is None
            else out_shape,
            fcompute=lambda i, j: tir.multiply(
                tir.subtract(
                    tir.Cast(
                        "float16",
                        tir.bitwise_and(
                            tir.shift_right(
                                weight[i, j // self.num_elem_per_storage],
                                tir.Cast(
                                    self.storage_dtype,
                                    (j % self.num_elem_per_storage)
                                    * DataType(self.quantize_dtype).bits,
                                ),
                            ),
                            tir_bin_mask,
                        ),
                    ),
                    tir.Cast(
                        "float16",
                        tir.bitwise_and(
                            tir.shift_right(
                                zeros[i, j // (self.group_size * self.num_elem_per_storage)],
                                tir.Cast(
                                    self.storage_dtype,
                                    (j // self.group_size % self.num_elem_per_storage)
                                    * DataType(self.quantize_dtype).bits,
                                ),
                            ),
                            tir_bin_mask,
                        ),
                    ),
                ),
                scale[i, j // self.group_size],
            ),
            name="decode",
        )


class AWQQuantizeLinear(nn.Module):  # pylint: disable=too-many-instance-attributes
    """An nn.Linear module with AWQ quantization"""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        in_features: int,
        out_features: int,
        config: AWQQuantize,
        bias: bool = True,
        out_dtype: Optional[str] = None,
    ) -> None:
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.out_dtype = out_dtype
        self.config = config
        self.qweight = nn.Parameter(
            (out_features, tir.ceildiv(in_features, config.num_elem_per_storage)),
            config.storage_dtype,
        )
        self.qzeros = nn.Parameter(
            (
                out_features,
                _calculate_zeros_width(in_features, config.group_size, config.num_elem_per_storage),
            ),
            dtype=config.storage_dtype,
        )
        self.scales = nn.Parameter(
            (
                out_features,
                _calculate_zeros_width(in_features, config.group_size, config.num_elem_per_storage)
                * config.num_elem_per_storage,
            ),
            config.model_dtype,
        )
        if bias:
            self.bias = nn.Parameter((out_features,), config.model_dtype)
        else:
            self.bias = None

    @staticmethod
    def from_linear(linear: nn.Linear, config: AWQQuantize) -> "AWQQuantizeLinear":
        """
        Converts a non-quantized nn.Linear to a group quantized AWQQuantizeLinear

        Parameters
        ----------
        linear : nn.Linear
            The non-quantized nn.Linear.

        config : AWQQuantize
            The awq quantization config.

        Returns
        -------
        ret : GroupQuantizeLinear
            The awq quantized AWQQuantizeLinear layer.
        """
        return AWQQuantizeLinear(
            in_features=linear.in_features,
            out_features=linear.out_features,
            config=config,
            bias=getattr(linear, "bias", None) is not None,
            out_dtype=linear.out_dtype,
        )

    def forward(self, x: nn.Tensor) -> nn.Tensor:  # pylint: disable=invalid-name
        """
        Forward method for awq quantized linear layer

        Parameters
        ----------
        x : nn.Tensor
            The input tensor.

        Returns
        -------
        ret : nn.Tensor
            The output tensor for the group quantized linear layer.
        """
        w = nn.op.tensor_expr_op(  # pylint: disable=invalid-name
            lambda weight, zeros, scale: self.config._dequantize(  # pylint: disable=protected-access
                weight,
                zeros,
                scale,
                [tir.IntImm("int64", self.out_features), tir.IntImm("int64", self.in_features)],
            ),
            name_hint="decode",
            args=[self.qweight, self.qzeros, self.scales],
        )
        w = nn.op.permute_dims(w)  # pylint: disable=invalid-name
        x = nn.op.matmul(x, w, out_dtype=self.out_dtype)
        if self.bias is not None:
            x = x + self.bias
        return x


class AWQQuantizeMultiLinear(nn.Module):  # pylint: disable=too-many-instance-attributes
    """An nn.MultiLinear module with awq quantization."""

    def __init__(  # pylint: disable=too-many-arguments
        self,
        in_features: int,
        out_features: nn.Sequence[int],
        config: AWQQuantize,
        bias: bool = True,
        out_dtype: Optional[str] = None,
    ):
        assert len(out_features) > 0
        self.total_out_features = sum(out_features)

        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.out_dtype = out_dtype
        self.config = config
        self.qweight = nn.Parameter(
            (self.total_out_features, tir.ceildiv(in_features, config.num_elem_per_storage)),
            config.storage_dtype,
        )
        self.qzeros = nn.Parameter(
            (
                self.total_out_features,
                _calculate_zeros_width(in_features, config.group_size, config.num_elem_per_storage),
            ),
            dtype=config.storage_dtype,
        )
        self.scales = nn.Parameter(
            (
                self.total_out_features,
                _calculate_zeros_width(in_features, config.group_size, config.num_elem_per_storage)
                * config.num_elem_per_storage,
            ),
            config.model_dtype,
        )
        if bias:
            self.bias = nn.Parameter((self.total_out_features,), config.model_dtype)
        else:
            self.bias = None

    @staticmethod
    def from_multilinear(
        multi_linear: nn.MultiLinear, config: AWQQuantize
    ) -> "AWQQuantizeMultiLinear":
        """
        Converts a non-quantized nn.MultiLinear to a awq quantized AWQQuantizeLinear.

        Parameters
        ----------
        linear : nn.MultiLinear
            The non-quantized nn.MultiLinear

        config : AWQQuantize
            The awq quantization config.

        Returns
        -------
        ret : AWQQuantizeMultiLinear
            The awq quantized AWQQuantizeMultiLinear layer.
        """
        return AWQQuantizeMultiLinear(
            in_features=multi_linear.in_features,
            out_features=multi_linear.out_features,
            config=config,
            bias=getattr(multi_linear, "bias", None) is not None,
            out_dtype=multi_linear.out_dtype,
        )

    def forward(self, x: nn.Tensor) -> Sequence[nn.Tensor]:  # pylint: disable=invalid-name
        """
        Forward method for multi linear layer.

        Parameters
        ----------
        x : Tensor
            The input tensor.

        Returns
        -------
        ret : Tensor
            The output tensor for the multi linear layer.
        """
        sections = list(np.cumsum(self.out_features)[:-1])
        w = nn.op.tensor_expr_op(  # pylint: disable=invalid-name
            lambda weight, zeros, scale: self.config._dequantize(  # pylint: disable=protected-access
                weight,
                zeros,
                scale,
                [
                    tir.IntImm("int64", self.total_out_features),
                    tir.IntImm("int64", self.in_features),
                ],
            ),
            name_hint="decode",
            args=[self.qweight, self.qzeros, self.scales],
        )
        w = nn.op.permute_dims(w)  # pylint: disable=invalid-name
        x = nn.op.matmul(x, w, out_dtype=self.out_dtype)
        if self.bias is not None:
            x = x + self.bias
        results = nn.op.split(x, sections, axis=-1)
        return results
