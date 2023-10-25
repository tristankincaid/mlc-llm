# pylint: disable=missing-docstring
import logging
from pathlib import Path
from typing import Union

import pytest
from mlc_chat.compiler import MODELS

# from mlc_chat.compiler.model.llama_config import LlamaConfig
# from mlc_chat.compiler.model.llama_parameter import huggingface
from mlc_chat.compiler.parameter import HuggingFaceLoader
from mlc_chat.support import tqdm

logging.basicConfig(
    level=logging.DEBUG,
    style="{",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="[{asctime}] {levelname} {filename}:{lineno}: {message}",
)


@pytest.mark.parametrize(
    "base_path",
    [
        "./dist/models/Llama-2-7b-hf",
        "./dist/models/Llama-2-13b-hf",
        "./dist/models/Llama-2-70b-hf",
    ],
)
def test_load_torch_llama(base_path: Union[str, Path]):
    base_path = Path(base_path)
    path_config = base_path / "config.json"
    path_params = base_path / "pytorch_model.bin.index.json"

    model = MODELS["llama"]
    config = model.config.from_file(path_config)
    loader = HuggingFaceLoader(
        path=path_params,
        extern_param_map=model.source["huggingface-torch"](config, None),
    )
    with tqdm.redirect():
        for _name, _param in loader.load():
            return  # To reduce the time of the test


@pytest.mark.parametrize(
    "base_path",
    [
        "./dist/models/Llama-2-7b-hf",
        "./dist/models/Llama-2-13b-hf",
        "./dist/models/Llama-2-70b-hf",
    ],
)
def test_load_safetensor_llama(base_path: Union[str, Path]):
    base_path = Path(base_path)
    path_config = base_path / "config.json"
    path_params = base_path / "model.safetensors.index.json"

    model = MODELS["llama"]
    config = model.config.from_file(path_config)
    loader = HuggingFaceLoader(
        path=path_params,
        extern_param_map=model.source["huggingface-safetensor"](config, None),
    )
    with tqdm.redirect():
        for _name, _param in loader.load():
            return  # To reduce the time of the test


if __name__ == "__main__":
    test_load_torch_llama(base_path="./dist/models/Llama-2-7b-hf")
    test_load_torch_llama(base_path="./dist/models/Llama-2-13b-hf")
    test_load_torch_llama(base_path="./dist/models/Llama-2-70b-hf")
    test_load_safetensor_llama(base_path="./dist/models/Llama-2-7b-hf")
    test_load_safetensor_llama(base_path="./dist/models/Llama-2-13b-hf")
    test_load_safetensor_llama(base_path="./dist/models/Llama-2-70b-hf")
