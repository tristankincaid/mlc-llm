"""Server context that shared by multiple entrypoint files."""

from typing import Dict, List, Optional

from ...chat_module import _get_model_path
from ...conversation_template import ConvTemplateRegistry
from ...protocol.conversation_protocol import Conversation
from .. import async_engine

from ...chat_module import _get_model_path


class ServerContext:
    """The global server context, including the running models
    and corresponding async engines.
    """

    _models: Dict[str, async_engine.AsyncThreadedEngine] = {}
    _conv_templates: Dict[str, Conversation] = {}
    _model_config_paths: Dict[str, str] = {}

    @staticmethod
    def add_model(hosted_model: str, engine: async_engine.AsyncThreadedEngine) -> None:
        """Add a new model to the server context together with the engine."""
        if hosted_model in ServerContext._models:
            raise RuntimeError(f"Model {hosted_model} already running.")
        ServerContext._models[hosted_model] = engine

        # Get the conversation template.
        if engine.conv_template_name is not None:
            conv_template = ConvTemplateRegistry.get_conv_template(engine.conv_template_name)
            if conv_template is not None:
                ServerContext._conv_templates[hosted_model] = conv_template

        _, config_file_path = _get_model_path(hosted_model)
        ServerContext._model_config_paths[hosted_model] = config_file_path

    @staticmethod
    def get_engine(model: str) -> Optional[async_engine.AsyncThreadedEngine]:
        """Get the async engine of the requested model."""
        return ServerContext._models.get(model, None)

    @staticmethod
    def get_conv_template(model: str) -> Optional[Conversation]:
        """Get the conversation template of the requested model."""
        conv_template = ServerContext._conv_templates.get(model, None)
        if conv_template is not None:
            return conv_template.model_copy(deep=True)
        return None

    @staticmethod
    def get_model_list() -> List[str]:
        """Get the list of models on serve."""
        return list(ServerContext._models.keys())

    @staticmethod
    def get_model_config_path(model: str) -> Optional[str]:
        """Get the model config path of the requested model."""
        return ServerContext._model_config_paths.get(model, None)
