import argparse
import asyncio
import os
import subprocess
import sys
from contextlib import asynccontextmanager

import tvm
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from dataclasses import dataclass, field, fields
from typing import Optional

from .chat_module import ChatModule
from .interface.openai_api import *


@dataclass
class RestAPIArgs:
    """RestAPIArgs is the dataclass that organizes the arguments used for starting a REST API server."""

    model: str = field(
        metadata={
            "help": (
                """
                The model folder after compiling with MLC-LLM build process. The parameter
                can either be the model name with its quantization scheme
                (e.g. ``Llama-2-7b-chat-hf-q4f16_1``), or a full path to the model
                folder. In the former case, we will use the provided name to search
                for the model folder over possible paths.
                """
            )
        }
    )
    lib_path: str = field(
        default="None",
        metadata={
            "help": (
                """
                The full path to the model library file to use (e.g. a ``.so`` file).
                """
            )
        }
    )
    device_name: str = field(
        default="auto",
        metadata={
            "help": (
                """
                The device name, enter one of "cuda", "metal", "vulkan", "rocm", "opencl", "auto".
                If "auto", the local device will be automatically detected.
                """
            )
        }
    )
    device_id: int = field(
        default=0,
        metadata={
            "help": (
                """
                The device id passed to ``tvm``, defaults to 0.
                """
            )
        }
    )
    host: str = field(
        default="127.0.0.1",
        metadata={
            "help": (
                """
                The host at which the server should be started, defaults to 127.0.0.1.
                """
            )
        }
    )
    port: int = field(
        default=8000,
        metadata={
            "help": (
                """
                The port on which the server should be started, defaults to 8000.
                """
            )
        }
    )

def convert_args_to_argparser() -> argparse.ArgumentParser:
    """Convert from RestAPIArgs to an equivalent ArgumentParser."""
    args = argparse.ArgumentParser("MLC Chat REST API")
    for field in fields(RestAPIArgs):
        name = field.name.replace("_", "-")
        field_name = f"--{name}"
        # `kwargs` contains `help`, `choices`, and `action`
        kwargs = field.metadata.copy()
        if field.type == bool:
            # boolean arguments do not need to specify `type`
            args.add_argument(field_name, default=field.default, **kwargs)
        else:
            args.add_argument(field_name, type=field.type, default=field.default, **kwargs)
    return args


session = {}

def _shared_lib_suffix():
    if sys.platform.startswith("linux") or sys.platform.startswith("freebsd"):
        return ".so"
    if sys.platform.startswith("win32"):
        return ".dll"
    if sys.platform.startswith("darwin"):
        cpu_brand_string = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode("utf-8")
        if cpu_brand_string.startswith("Apple"):
            # Apple Silicon
            return ".so"
        else:
            # Intel (x86)
            return ".dylib"
    return ".so"


@asynccontextmanager
async def lifespan(app: FastAPI):
    chat_mod = ChatModule(
        model=ARGS.model,
        device_name=ARGS.device_name,
        device_id=ARGS.device_id,
        lib_path=ARGS.lib_path
    )
    session["chat_mod"] = chat_mod

    yield

    session.clear()


app = FastAPI(lifespan=lifespan)

class AsyncChatCompletionStream:
    def __aiter__(self):
        return self

    async def get_next_msg(self):
        if not session["chat_mod"].stopped():
            session["chat_mod"].decode()
            msg = session["chat_mod"].get_message()
            return msg
        else:
            raise StopAsyncIteration

    async def __anext__(self):
        if not session["chat_mod"].stopped():
            task = asyncio.create_task(self.get_next_msg())
            msg = await task
            return msg
        else:
            raise StopAsyncIteration


@app.post("/v1/chat/completions")
async def request_completion(request: ChatCompletionRequest):
    """
    Creates model response for the given chat conversation.
    """
    for message in request.messages:
        session["chat_mod"].prefill(input=message.content)
    if request.stream:

        async def iter_response():
            prev_txt = ""
            async for content in AsyncChatCompletionStream():
                if content:
                    chunk = ChatCompletionStreamResponse(
                        choices=[
                            ChatCompletionResponseStreamChoice(
                                index=0,
                                delta=DeltaMessage(
                                    role="assistant", content=content[len(prev_txt) :]
                                ),
                                finish_reason="stop",
                            )
                        ]
                    )
                    prev_txt = content
                    yield f"data: {chunk.json(exclude_unset=True)}\n\n"

        return StreamingResponse(iter_response(), media_type="text/event-stream")
    else:
        msg = None
        while not session["chat_mod"].stopped():
            session["chat_mod"].decode()
            msg = session["chat_mod"].get_message()
        return ChatCompletionResponse(
            choices=[
                ChatCompletionResponseChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=msg),
                    finish_reason="stop",
                )
            ],
            # TODO: Fill in correct usage info
            usage=UsageInfo(prompt_tokens=0, completion_tokens=0, total_tokens=0),
        )


@app.post("/v1/completions")
async def request_completion(request: CompletionRequest):
    """
    Creates a completion for a given prompt.
    """
    session["chat_mod"].reset_chat()
    # Langchain's load_qa_chain.run expects the input to be a list with the query
    if isinstance(request.prompt, list):
        prompt = request.prompt[0]
    else:
        prompt = request.prompt
    session["chat_mod"].prefill(input=prompt)

    msg = None
    while not session["chat_mod"].stopped():
        session["chat_mod"].decode()
        msg = session["chat_mod"].get_message()
    return CompletionResponse(
        choices=[CompletionResponseChoice(index=0, text=msg)],
        # TODO: Fill in correct usage info
        usage=UsageInfo(prompt_tokens=0, completion_tokens=0, total_tokens=0),
    )


@app.post("/v1/embeddings")
async def request_embeddings(request: EmbeddingsRequest):
    """
    Gets embedding for some text.
    """
    assert "Endpoint not implemented."


@app.post("/chat/reset")
async def reset():
    """
    Reset the chat for the currently initialized model.
    """
    session["chat_mod"].reset_chat()


@app.get("/stats")
async def read_stats():
    """
    Get the runtime stats.
    """
    return session["chat_mod"].runtime_stats_text()


ARGS = convert_args_to_argparser().parse_args()
if __name__ == "__main__":
    uvicorn.run("mlc_chat.rest:app", host=ARGS.host, port=ARGS.port, reload=False, access_log=False)
