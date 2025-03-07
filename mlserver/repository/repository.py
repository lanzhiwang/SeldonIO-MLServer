import abc
import os
import glob

from pydantic.error_wrappers import ValidationError
from typing import List

from ..settings import ModelParameters, ModelSettings
from ..errors import ModelNotFound
from ..logging import logger

from .load import load_model_settings

DEFAULT_MODEL_SETTINGS_FILENAME = "model-settings.json"


class ModelRepository(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def list(self) -> List[ModelSettings]:
        raise NotImplementedError

    @abc.abstractmethod
    async def find(self, name: str) -> List[ModelSettings]:
        raise NotImplementedError


class SchemalessModelRepository(ModelRepository):
    """
    Model repository, responsible of the discovery of models which can be
    loaded onto the model registry.
    """

    def __init__(self, root: str):
        # self._root='./example/02-Serving-HuggingFace-models/'
        self._root = root

    async def list(self) -> List[ModelSettings]:
        all_model_settings = []

        # print("repository repository list self._root:", self._root)
        # repository repository list self._root: ./example/02-Serving-HuggingFace-models/

        # TODO: Use an async alternative for filesys ops
        if self._root:
            abs_root = os.path.abspath(self._root)
            # print("repository repository list abs_root:", abs_root)
            # repository repository list abs_root: /workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models

            pattern = os.path.join(abs_root, "**", DEFAULT_MODEL_SETTINGS_FILENAME)
            # print("repository repository list pattern:", pattern)
            # repository repository list pattern: /workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models/**/model-settings.json

            matches = glob.glob(pattern, recursive=True)
            # print("repository repository list matches:", matches)
            # repository repository list matches: ['/workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models/model-settings.json']

            for model_settings_path in matches:
                # print("repository repository list model_settings_path:", model_settings_path)
                # repository repository list model_settings_path: /workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models/model-settings.json

                try:
                    model_settings = load_model_settings(model_settings_path)
                    # print("repository repository list model_settings:", model_settings)
                    # repository repository list model_settings: name='transformer' platform='' versions=[] inputs=[] outputs=[] parallel_workers=None warm_workers=False max_batch_size=0 max_batch_time=0.0 implementation_='mlserver_huggingface.HuggingFaceRuntime' parameters=ModelParameters(uri='/workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models', version=None, environment_tarball=None, format=None, content_type=None, extra={'task': 'text-generation', 'pretrained_model': 'distilgpt2'}) cache_enabled=False

                    all_model_settings.append(model_settings)
                except Exception:
                    logger.exception(
                        f"Failed load model settings at {model_settings_path}."
                    )

        # If there were no matches, try to load model from environment
        if not all_model_settings:
            logger.debug(f"No models were found in repository at {self._root}.")
            try:
                # return default
                model_settings = ModelSettings()
                model_settings.parameters = ModelParameters()
                all_model_settings.append(model_settings)
            except ValidationError:
                logger.debug("No default model found in environment settings.")

        return all_model_settings

    async def find(self, name: str) -> List[ModelSettings]:
        all_settings = await self.list()
        selected = []
        for model_settings in all_settings:
            # TODO: Implement other version policies (e.g. "Last N")
            if model_settings.name == name:
                selected.append(model_settings)

        if len(selected) == 0:
            raise ModelNotFound(name)

        return selected
