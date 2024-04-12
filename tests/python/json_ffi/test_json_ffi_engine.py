# pylint: disable=chained-comparison,line-too-long,missing-docstring,
# pylint: disable=too-many-arguments,too-many-locals,unused-argument,unused-variable
import json
import queue
import threading
from typing import Any, Callable, Dict, Iterator, List, Literal, Optional, Union

import tvm

from mlc_llm.protocol import openai_api_protocol
from mlc_llm.serve import engine_utils
from mlc_llm.serve.engine_base import (
    EngineConfig,
    _infer_kv_cache_config,
    _parse_models,
    _process_model_args,
    detect_device,
)
from mlc_llm.tokenizer import Tokenizer

prompts = [
    "What is the meaning of life?",
    "Introduce the history of Pittsburgh to me. Please elaborate in detail.",
    "Write a three-day Seattle travel plan. Please elaborate in detail.",
    "What is Alaska famous of? Please elaborate in detail.",
    "What is the difference between Lambda calculus and Turing machine? Please elaborate in detail.",
    "What are the necessary components to assemble a desktop computer? Please elaborate in detail.",
    "Why is Vitamin D important to human beings? Please elaborate in detail.",
    "Where is milk tea originated from? Please elaborate in detail.",
    "Where is the southernmost place in United States? Please elaborate in detail.",
    "Do you know AlphaGo? What capabilities does it have, and what achievements has it got? Please elaborate in detail.",
]


class EngineState:
    sync_queue: queue.Queue

    def get_request_stream_callback(self) -> Callable[[List[str]], None]:
        # ChatCompletionStreamResponse

        def _callback(chat_completion_stream_responses_json_str: List[str]) -> None:
            self._sync_request_stream_callback(chat_completion_stream_responses_json_str)

        return _callback

    def _sync_request_stream_callback(
        self, chat_completion_stream_responses_json_str: List[str]
    ) -> None:
        # Put the delta outputs to the queue in the unblocking way.
        self.sync_queue.put_nowait(chat_completion_stream_responses_json_str)


class JSONFFIEngine:
    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        model: str,
        device: Union[str, tvm.runtime.Device] = "auto",
        *,
        model_lib_path: Optional[str] = None,
        mode: Literal["local", "interactive", "server"] = "local",
        additional_models: Optional[List[str]] = None,
        max_batch_size: Optional[int] = None,
        max_total_sequence_length: Optional[int] = None,
        prefill_chunk_size: Optional[int] = None,
        engine_config: Optional[EngineConfig] = None,
        gpu_memory_utilization: Optional[float] = None,
    ) -> None:
        # - Initialize model loading info.
        models = _parse_models(model, model_lib_path, additional_models)
        if isinstance(device, str):
            device = detect_device(device)
        assert isinstance(device, tvm.runtime.Device)
        (
            model_args,
            model_config_paths,
            tokenizer_path,
            self.conv_template,
        ) = _process_model_args(models, device)

        # - Load the raw model config into dict
        self.model_config_dicts = []
        for i, model_info in enumerate(models):
            # model_args:
            # [model_lib_path, model_path, device.device_type, device.device_id] * N
            model_info.model_lib_path = model_args[i * (len(model_args) // len(models))]
            with open(model_config_paths[i], "r", encoding="utf-8") as file:
                self.model_config_dicts.append(json.load(file))

        # - Decide the KV cache config based on mode and user input.
        kv_cache_config, max_single_sequence_length = _infer_kv_cache_config(
            mode,
            max_batch_size,
            max_total_sequence_length,
            prefill_chunk_size,
            gpu_memory_utilization,
            models,
            device,
            self.model_config_dicts,
            model_config_paths,
        )
        self.max_input_sequence_length = min(
            max_single_sequence_length, kv_cache_config.max_total_sequence_length
        )

        # - Initialize engine state and engine.
        self.state = EngineState()
        module = tvm.get_global_func("mlc.json_ffi.CreateJSONFFIEngine", allow_missing=False)()
        self._ffi = {
            key: module[key]
            for key in [
                "init_background_engine",
                "chat_completion",
                "abort",
                "get_last_error",
                "run_background_loop",
                "run_background_stream_back_loop",
                "exit_background_loop",
            ]
        }
        self.tokenizer = Tokenizer(tokenizer_path)
        if engine_config is None:
            # The default engine mode: non-speculative
            engine_config = EngineConfig()

        def _background_loop():
            self._ffi["init_background_engine"](
                max_single_sequence_length,
                tokenizer_path,
                kv_cache_config.asjson(),
                engine_config.asjson(),
                self.state.get_request_stream_callback(),
                None,
                *model_args,
            )
            self._ffi["run_background_loop"]()

        def _background_stream_back_loop():
            self._ffi["run_background_stream_back_loop"]()

        # Create the background engine-driving thread and start the loop.
        self._background_loop_thread: threading.Thread = threading.Thread(target=_background_loop)
        self._background_stream_back_loop_thread: threading.Thread = threading.Thread(
            target=_background_stream_back_loop
        )
        self._background_loop_thread.start()
        self._background_stream_back_loop_thread.start()
        self._terminated = False

    def terminate(self):
        self._terminated = True
        self._ffi["exit_background_loop"]()
        self._background_loop_thread.join()
        self._background_stream_back_loop_thread.join()

    def chat_completion(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        *,
        messages: List[Dict[str, Any]],
        model: str,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        logprobs: bool = False,
        top_logprobs: int = 0,
        logit_bias: Optional[Dict[int, float]] = None,
        max_tokens: Optional[int] = None,
        n: int = 1,
        seed: Optional[int] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        temperature: float = 1.0,
        top_p: float = 1.0,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[Literal["none", "auto"], Dict]] = None,
        user: Optional[str] = None,
        ignore_eos: bool = False,
        response_format: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> Iterator[openai_api_protocol.ChatCompletionStreamResponse]:
        if request_id is None:
            request_id = f"chatcmpl-{engine_utils.random_uuid()}"

        chatcmpl_generator = self._handle_chat_completion(
            openai_api_protocol.ChatCompletionRequest(
                messages=[
                    openai_api_protocol.ChatCompletionMessage.model_validate(message)
                    for message in messages
                ],
                model=model,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                logprobs=logprobs,
                top_logprobs=top_logprobs,
                logit_bias=logit_bias,
                max_tokens=max_tokens,
                n=n,
                seed=seed,
                stop=stop,
                stream=stream,
                temperature=temperature,
                top_p=top_p,
                tools=(
                    [openai_api_protocol.ChatTool.model_validate(tool) for tool in tools]
                    if tools is not None
                    else None
                ),
                tool_choice=tool_choice,
                user=user,
                ignore_eos=ignore_eos,
                response_format=(
                    openai_api_protocol.RequestResponseFormat.model_validate(response_format)
                    if response_format is not None
                    else None
                ),
            ).model_dump_json(),
            n=n,
            request_id=request_id,
        )
        for response in chatcmpl_generator:
            yield response

    def _handle_chat_completion(
        self, request_json_str: str, n: int, request_id: str
    ) -> Iterator[openai_api_protocol.ChatCompletionStreamResponse]:
        self.state.sync_queue = queue.Queue()
        num_unfinished_requests = n

        success = bool(self._ffi["chat_completion"](request_json_str, request_id))

        try:
            while num_unfinished_requests > 0:
                chat_completion_stream_responses_json_str = self.state.sync_queue.get()
                for chat_completion_response_json_str in chat_completion_stream_responses_json_str:
                    chat_completion_response = (
                        openai_api_protocol.ChatCompletionStreamResponse.model_validate_json(
                            chat_completion_response_json_str
                        )
                    )
                    for choice in chat_completion_response.choices:
                        if choice.finish_reason is not None:
                            num_unfinished_requests -= 1
                    yield chat_completion_response
        except Exception as exception:  # pylint: disable=broad-exception-caught
            self._ffi["abort"](request_id)
            raise exception


def test_chat_completion(engine: JSONFFIEngine):
    num_requests = 2
    max_tokens = 64
    n = 1
    output_texts: List[List[str]] = [["" for _ in range(n)] for _ in range(num_requests)]

    for rid in range(num_requests):
        print(f"chat completion for request {rid}")
        for response in engine.chat_completion(
            messages=[{"role": "user", "content": [{"type": "text", "text": prompts[rid]}]}],
            model=model,
            max_tokens=max_tokens,
            n=n,
            request_id=str(rid),
        ):
            for choice in response.choices:
                assert choice.delta.role == "assistant"
                assert isinstance(choice.delta.content[0], Dict)
                assert choice.delta.content[0]["type"] == "text"
                output_texts[rid][choice.index] += choice.delta.content[0]["text"]

    # Print output.
    print("Chat completion all finished")
    for req_id, outputs in enumerate(output_texts):
        print(f"Prompt {req_id}: {prompts[req_id]}")
        if len(outputs) == 1:
            print(f"Output {req_id}:{outputs[0]}\n")
        else:
            for i, output in enumerate(outputs):
                print(f"Output {req_id}({i}):{output}\n")


def test_malformed_request(engine: JSONFFIEngine):
    for response in engine._handle_chat_completion("malformed_string", n=1, request_id="123"):
        assert len(response.choices) == 1
        assert response.choices[0].finish_reason == "error"


if __name__ == "__main__":
    # Create engine.
    model = "dist/Llama-2-7b-chat-hf-q0f16-MLC"
    model_lib_path = "dist/Llama-2-7b-chat-hf-q0f16-MLC/Llama-2-7b-chat-hf-q0f16-MLC-cuda.so"
    engine = JSONFFIEngine(
        model,
        model_lib_path=model_lib_path,
        max_total_sequence_length=1024,
    )

    test_chat_completion(engine)
    test_malformed_request(engine)

    engine.terminate()
    del engine
