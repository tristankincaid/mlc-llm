"""Chat module for MLC chat in a standalone file, including image module for multimodal-purposes."""
#! pylint: disable=unused-import, invalid-name
import ctypes
import json
import os
import sys
from dataclasses import dataclass, fields, asdict
from enum import Enum
from typing import List, Optional

import tvm
import tvm._ffi.base

from . import libinfo

# pylint: disable=line-too-long
_PYTHON_GET_STARTED_TUTORIAL_URL = "https://github.com/mlc-ai/notebooks/blob/main/mlc-llm/tutorial_chat_module_getting_started.ipynb"
# pylint: enable=line-too-long


def _load_mlc_llm_lib():
    """Load mlc llm lib"""
    if sys.platform.startswith("win32") and sys.version_info >= (3, 8):
        for path in libinfo.get_dll_directories():
            os.add_dll_directory(path)
    lib_name = "mlc_llm" if tvm._ffi.base._RUNTIME_ONLY else "mlc_llm_module"
    lib_path = libinfo.find_lib_path(lib_name, optional=False)
    return ctypes.CDLL(lib_path[0]), lib_path[0]


# only load once here
if os.environ.get("SKIP_LOADING_MLCLLM_SO", "0") == "0":
    _LIB, _LIB_PATH = _load_mlc_llm_lib()


def quantization_keys():
    return [
        "q3f16_0",
        "q4f16_0",
        "q4f16_1",
        "q4f32_0",
        "q8f16_0",
        "q0f16",
        "q0f32",
    ]


# TODO(Charlie): add documentation for the two dataclasses looking at
# https://mlc.ai/mlc-llm/docs/get_started/mlc_chat_config.html
@dataclass
class ConvConfig:
    """The dataclass that represents conversation template."""

    # Everything has to be optional since users do not have to override
    name: Optional[str] = None
    system: Optional[str] = None
    roles: Optional[List[str]] = None
    messages: Optional[List[str]] = None
    offset: Optional[str] = None
    separator_style: Optional[int] = None
    seps: Optional[List[str]] = None
    role_msg_sep: Optional[str] = None
    role_empty_sep: Optional[str] = None
    role_msg_sep: Optional[str] = None  # TODO(Charlie): not present in `llm_chat.cc`
    stop_str: Optional[str] = None
    stop_tokens: Optional[List[int]] = None
    add_bos: Optional[bool] = None


# TODO(Charlie): determine what is optional and what is not here
@dataclass
class ChatConfig:
    """The dataclass that represents the mlc-chat-config.json file."""

    # Everything has to be optional since users do not have to override
    model_lib: Optional[str] = None
    local_id: Optional[str] = None
    conv_template: Optional[str] = None
    temperature: Optional[float] = None
    repetition_penalty: Optional[float] = None
    top_p: Optional[float] = None
    mean_gen_len: Optional[int] = None
    max_gen_len: Optional[int] = None
    shift_fill_factor: Optional[float] = None
    tokenizer_files: Optional[List[str]] = None
    conv_config: Optional[ConvConfig] = None
    model_category: Optional[str] = None
    model_name: Optional[str] = None


class PlaceInPrompt(Enum):
    """The place of an input message in a prompt."""

    # The input message should have role names and corresponding seperators appended both prior to it and after it,
    # making it a complete prompt.
    All = 0
    # The input message is only the beginning part of a prompt, no role name and separator should be appended after
    # the message since there will be future messages appended after the message.
    Begin = 1
    # The input message is in the middle of a prompt, nothing should be appended before or after the message.
    Middle = 2
    # The input message is the ending part of a prompt, no role name and separator should be appended prior to it
    # since the message is concatenated to some prior messages.
    End = 3

def _convert_chat_config_to_json_str(chat_config: ChatConfig, conv_template: str):
    """Convert user's input ChatConfig to a json string."""
    if chat_config is None:
        return ""
    # Current logic does not allow partial ChatConfig wihtout specifying the
    # conv_template. Hence we use the conv_template after considering overrides.
    chat_config.conv_template = conv_template
    # Only want to keep entries that are not None; otherwise, we would override things to None
    assert hasattr(ChatConfig, "conv_config")  # in case dataclass attribute name changes
    chat_dict = {}
    for k, v in asdict(chat_config).items():
        if k == "conv_config" and v is not None:
            # conv template is another dict, do the same thing
            conv_dict = {}
            for conv_k, conv_v in v.items():
                if conv_v is not None:
                    conv_dict[conv_k] = conv_v
            chat_dict[k] = conv_dict
            continue

        if v is not None:
            chat_dict[k] = v

    return json.dumps(chat_dict)


class ChatModule:
    def __init__(
        self,
        model,
        device_name: str = "cuda",
        device_id: int = 0,
        chat_config: Optional[ChatConfig] = None,
        lib_path=None,
    ):
        r"""Initialize a chat module.

        Parameters
        ----------
        model: str
            The huggingface model name with its quantization. Or the full path
            to a folder of such weights.
        target : str
            The target device type.
        device_id : int
            The device id.
        """
        # 1. Get self.device
        if device_name == "cuda":
            self.device = tvm.cuda(device_id)
        elif device_name == "metal":
            self.device = tvm.metal(device_id)
        elif device_name == "vulkan":
            self.device = tvm.vulkan(device_id)
        elif device_name == "rocm":
            self.device = tvm.rocm(device_id)
        elif device_name == "opencl":
            self.device = tvm.opencl(device_id)
        else:
            raise ValueError("device type not supported yet")
        device_type = self.device.device_type

        # 2. Populate chat/image mod and their functions
        fcreate_chat_mod = tvm.get_global_func("mlc.llm_chat_create")
        assert fcreate_chat_mod is not None
        chat_mod = fcreate_chat_mod(device_type, device_id)
        fcreate_image_mod = tvm.get_global_func("mlc.llm_image_module_create")
        assert fcreate_image_mod is not None
        image_mod = fcreate_image_mod(device_type, device_id)

        # chat module related functions
        self.reload_func = chat_mod["reload"]
        self.prefill_func = chat_mod["prefill"]
        self.embed_func = chat_mod["embed"]
        self.prefill_with_embed_func = chat_mod["prefill_with_embed"]
        self.decode_func = chat_mod["decode"]
        self.stopped_func = chat_mod["stopped"]
        self.get_message_func = chat_mod["get_message"]
        self.reset_chat_func = chat_mod["reset_chat"]
        self.runtime_stats_text_func = chat_mod["runtime_stats_text"]
        self.reset_runtime_stats_func = chat_mod["reset_runtime_stats"]
        self.process_system_prompts_func = chat_mod["process_system_prompts"]
        self.evaluate_func = chat_mod["evaluate"]
        self.get_role0 = chat_mod["get_role0"]
        self.get_role1 = chat_mod["get_role1"]

        # image module related functions
        self.image_reload_func = image_mod["reload"]
        self.image_embed_func = image_mod["embed"]
        self.image_reset_func = image_mod["reset"]
        self.image_runtime_stats_text_func = image_mod["runtime_stats_text"]
        self.image_reset_runtime_stats_func = image_mod["reset_runtime_stats"]

        # 3. Look up model_path
        self.model_path, self.config_file_path = self._get_model_path(model)

        # 4. Instantiate chat_config
        self.chat_config = self._get_chat_config(self.config_file_path, chat_config)

        # 5. Look up model library
        self.lib_path = self._get_lib_path(model, self.chat_config, lib_path, device_name)

        # 6. Call reload
        # TODO(Charlie): check if this method will serialize the ConvConfig
        user_chat_config_json_str = _convert_chat_config_to_json_str(chat_config, self.chat_config.conv_template)
        self._reload(self.lib_path, self.model_path, user_chat_config_json_str)

    def _get_lib_path(
        self, model: str, chat_config: ChatConfig, lib_path: Optional[str], device_name: str
    ) -> str:
        """Look up the model library."""
        # 1. Use user's lib_path if provided
        if lib_path is not None:
            if os.path.isfile(lib_path):
                print(f"Using library model: {lib_path}")
                lib_path = tvm.runtime.load_module(lib_path)
                return lib_path
            else:
                err_msg = (
                    f"The `lib_path` you passed in is not a file: {lib_path}.\nPlease checkout "
                    f"{_PYTHON_GET_STARTED_TUTORIAL_URL} for an example on how to load a model."
                )
                raise FileNotFoundError(err_msg)

        # 2. Generate all possible file names according to OS
        candidate_lib_names = []
        if sys.platform.startswith("linux"):
            candidate_lib_names = [f"{chat_config.model_lib}-{device_name}.so"]
        elif sys.platform.startswith("Darwin"):
            # Note that `dylib` comes before `so` since we prioritize `dylib` for MacOS
            candidate_lib_names = [
                f"{chat_config.model_lib}-{device_name}.dylib",
                f"{chat_config.model_lib}-{device_name}.so",
            ]
        elif sys.platform.startswith("win32"):
            candidate_lib_names = [f"{chat_config.model_lib}-{device_name}.dll"]
        else:
            candidate_lib_names = [
                f"{chat_config.model_lib}-{device_name}.dylib",
                f"{chat_config.model_lib}-{device_name}.so",
                f"{chat_config.model_lib}-{device_name}.dll",
            ]

        # 3. Genereate possible model library paths
        candidate_paths = []
        for lib_name in candidate_lib_names:
            # TODO(Charlie): There should be more possibilities (e.g. using self.model_path)
            candidate_paths.extend(
                [
                    f"{lib_name}",
                    f"dist/prebuilt/lib/{lib_name}",  # Using prebuilt workflow
                    f"dist/{model}/{lib_name}",  # Default directory after mlc_llm.build_model()
                ]
            )

        # 4. Search for model library
        for candidate in candidate_paths:
            if os.path.isfile(candidate):
                print(f"Using library model: {os.path.abspath(candidate)}")
                candidate_loaded = tvm.runtime.load_module(candidate)
                return candidate_loaded

        # 5. Error
        err_msg = (
            f"Cannot find the library that corresponds to {chat_config.model_lib}, "
            "which is either provided in the `chat_config` you passed in, or "
            f"specified in {self.config_file_path}.\n"
            "We searched over: \n"
        )
        for candidate in candidate_paths:
            err_msg += f"- {candidate}\n"
        err_msg += (
            "If you would like to directly specify the model lib path, you may "
            "consider passing in the `lib_path` parameter.\n"
            f"Please checkout {_PYTHON_GET_STARTED_TUTORIAL_URL} for an example "
            "on how to load a model."
        )
        raise FileNotFoundError(err_msg)

    def _get_chat_config(self, config_file_path: str, user_chat_config: ChatConfig) -> ChatConfig:
        """Read the config file in model path, potentially overriden by user input."""
        original_chat_config = None
        with open(config_file_path, mode="rt", encoding="utf-8") as f:
            json_object = json.load(f)
            original_chat_config = ChatConfig(**json_object)
        if user_chat_config is not None:
            # We override using user's chat config
            for field in fields(user_chat_config):
                field_name = field.name
                field_value = getattr(user_chat_config, field_name)
                if field_value is not None:
                    setattr(original_chat_config, field_name, field_value)
        return original_chat_config

    def _get_model_path(self, model: str) -> (str, str):
        """Use user-provided ``model`` to search for a valid model path.

        We define "valid" as having an ``mlc-chat-config.json`` right under the folder.

        Raises error messages with information and hints for users.

        Parameters
        ----------
        model : str
            User' input.

        Returns
        ------
        model_path : str
            A "valid" model_path, with ``os.isfile(os.path.join(model_path,
            "mlc-chat-config.json"))`` being ``True``.
        chat_file : str
            Essentially ``os.path.join(model_path, "mlc-chat-config.json")``.
        """
        # Note that the order of this list corresponds to our search priority
        candidate_paths = [
            f"{model}",  # full path, or just the name
            f"dist/prebuilt/{model}",  # Using prebuilt workflow
            f"dist/{model}/params",  # Default directory after mlc_llm.build_model()
            f"dist/prebuilt/mlc-chat-{model}",  # Also prebuilt workflow, but missed prefix
        ]

        # Look for the first folder that has `mlc-chat-config.json` under it
        for candidate in candidate_paths:
            chat_file = os.path.join(candidate, "mlc-chat-config.json")
            if os.path.isfile(chat_file):
                print(f"Using model folder: {os.path.abspath(candidate)}")
                return candidate, chat_file

        # Failed to find a valid model_path, analyzing error for user
        err_msg = (
            "Cannot find mlc-chat-config.json in the model folder. "
            "According to your input `model`, we found folder(s): "
        )
        found_folder = False
        for candidate in candidate_paths:
            if os.path.isdir(candidate):
                err_msg += f"- {os.path.abspath(candidate)}\n"
                found_folder = True

        if found_folder:
            # Error 1: there is a folder, but not an mlc-llm model folder
            err_msg += (
                "But we cannot find `mlc-chat-config.json` in the folder(s), a required file.\n"
                "MLC-Chat consumes models that are processed "
                "by the MLC-LLM build process. Please checkout "
                f"{_PYTHON_GET_STARTED_TUTORIAL_URL} for an example on how to load a model."
            )
            raise FileNotFoundError(err_msg)
        else:
            # Error 2: cannot find a folder
            err_msg = (
                "Cannot find the model folder. We searched over the following possible paths: "
                f"{candidate_paths}.\n"
                "You can try to pass in `model=/path/to/your-model-path`, and confirm "
                "that it contains `mlc-chat-config.json`. Please checkout "
                f"{_PYTHON_GET_STARTED_TUTORIAL_URL} for an example on how to load a model."
            )
            raise FileNotFoundError(err_msg)

    def _reload(self, lib: str, model_path: str, app_config_json: str = ""):
        r"""Reload the chat module from the given library and model path.

        Parameters
        ----------
        lib : str
            The library path.
        model_path : str
            The model path.
        app_config_json: str
            The partial config that is used to partially override the model configuration.
        """
        self.reload_func(lib, model_path, app_config_json)

    def prefill(
        self,
        input: str,
        decode_next_token: bool = True,
        place_in_prompt: PlaceInPrompt = PlaceInPrompt.All,
    ):
        r"""Run prefill stage for a given input and optionally decode the first output token.
        User can decide where to place the input in the prompt.

        Parameters
        ----------
        input : str
            The user input string.
        decode_next_token : bool
            Whether to decode the next token after prefilling.
        place_in_prompt: PlaceInPrompt
            The place of the input message in the prompt.
        """
        self.prefill_func(input, decode_next_token, place_in_prompt.value)

    def embed(
        self,
        input: str,
        place_in_prompt: PlaceInPrompt = PlaceInPrompt.All,
    ):
        r"""Given a text input, get the embedding of the tokenized prompt.
        User can decide where to place the input in the prompt.

        Parameters
        ----------
        input : str
            The user input string.
        place_in_prompt: PlaceInPrompt
            The place of the input message in the prompt.
        """
        return self.embed_func(input, place_in_prompt.value)

    def prefill_with_embed(self, embedding: tvm.runtime.NDArray, decode_next_token: bool = True):
        r"""Given an embedding, run the prefill stage and optionally decode the first output token.

        Parameters
        ----------
        embedding : tvm.runtime.NDArray
            The embedding of user input.
        decode_next_token : bool
            Whether to decode the next token after prefilling.
        """
        self.prefill_with_embed_func(embedding, decode_next_token)

    def decode(self):
        r"""Decode the next token, the decoding result is stored in a buffer and
        can be retrieved by :func:`get_message`.
        """
        self.decode_func()

    def stopped(self) -> bool:
        r"""Check if the stop condition is met for the current round.

        Returns
        -------
        stopped : bool
        """
        return self.stopped_func() != 0

    def get_message(self) -> str:
        r"""Get the output message in the current round.

        Returns
        -------
        message : str

        Note
        ----
        This function returns the message that corresponds to
        all the tokens decoded so far.
        """
        return self.get_message_func()

    def reset_chat(self):
        r"""Reset the chat session and clear all chat history.

        Note
        ----
        The model remains the same after :func:`reset_chat`.
        To reload module, please use :func:`reload` instead.
        """
        self.reset_chat_func()

    def runtime_stats_text(self) -> str:
        r"""Get the runtime stats text (encoding speed and decoding speed).

        Returns
        -------
        stats : str
            The runtime stats text.
        """
        return self.runtime_stats_text_func()

    def reset_runtime_stats(self):
        r"""Reset the runtime stats."""
        self.reset_runtime_stats_func()

    def process_system_prompts(self):
        r"""Pre-process by prefilling the system prompts, running prior to any user input."""
        self.process_system_prompts_func()

    def evaluate(self):
        self.evaluate_func()

    def reload_image_module(self, lib: str, model_path: str):
        r"""Reload the image module from the given library and model path.

        Parameters
        ----------
        lib : str
            The library path.
        model_path : str
            The model path.
        """
        self.reload_func(lib, model_path)

    def reset_image_module(self):
        r"""Reset the image module, clear its performance record.

        Note
        ----
        The model remains the same after :func:`reset_image_module`.
        To reload module, please use :func:`reload` instead.
        """
        self.reset_image_module_func()

    def get_image_embedding(
        self,
        image: tvm.runtime.NDArray,
    ):
        r"""Given an image of type NDArray, get the embedding of the image.

        Parameters
        ----------
        image : tvm.runtime.NDArray
            The user uploaded image.
        """
        return self.embed_func(image)

    def image_module_runtime_stats_text(self) -> str:
        r"""Get the runtime stats text (image encoding speed).

        Returns
        -------
        stats : str
            The runtime stats text.
        """
        return self.runtime_stats_text_func()

    def reset_image_module_runtime_stats(self):
        r"""Reset the runtime stats."""
        self.reset_runtime_stats_func()
