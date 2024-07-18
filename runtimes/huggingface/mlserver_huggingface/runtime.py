import asyncio
import torch

from mlserver.model import MLModel
from mlserver.settings import ModelSettings
from mlserver.logging import logger
from mlserver.types import (
    InferenceRequest,
    InferenceResponse,
)

from .settings import get_huggingface_settings
from .common import load_pipeline_from_settings
from .codecs import HuggingfaceRequestCodec
from .metadata import METADATA


class HuggingFaceRuntime(MLModel):
    """Runtime class for specific Huggingface models"""

    def __init__(self, settings: ModelSettings):
        self.hf_settings = get_huggingface_settings(settings)
        super().__init__(settings)

    async def load(self) -> bool:
        # Loading & caching pipeline in asyncio loop to avoid blocking
        logger.info(f"Loading model for task '{self.hf_settings.task_name}'...")
        await asyncio.get_running_loop().run_in_executor(
            None,
            load_pipeline_from_settings,
            self.hf_settings,
            self.settings,
        )

        # Now we load the cached model which should not block asyncio
        self._model = load_pipeline_from_settings(self.hf_settings, self.settings)
        self._merge_metadata()
        return True

    async def predict(self, payload: InferenceRequest) -> InferenceResponse:
        # print("runtime huggingface runtime predict payload:", payload)
        # runtime huggingface runtime predict payload:
        #     id='d8e57b8b-1082-4340-b41f-0d3d3f87a3bc'
        #     parameters=Parameters(
        #         content_type=None,
        #         headers={
        #             'host': 'localhost:8080',
        #             'user-agent': 'python-requests/2.31.0',
        #             'accept-encoding': 'gzip, deflate, br',
        #             'accept': '*/*',
        #             'connection': 'keep-alive',
        #             'content-length': '93',
        #             'content-type': 'application/json',
        #             'Ce-Specversion': '0.3',
        #             'Ce-Source': 'io.seldon.serving.deployment.mlserver',
        #             'Ce-Type': 'io.seldon.serving.inference.request',
        #             'Ce-Modelid': 'transformer',
        #             'Ce-Inferenceservicename': 'mlserver',
        #             'Ce-Endpoint': 'transformer',
        #             'Ce-Id': 'd8e57b8b-1082-4340-b41f-0d3d3f87a3bc',
        #             'Ce-Requestid': 'd8e57b8b-1082-4340-b41f-0d3d3f87a3bc'
        #         }
        #     )
        #     inputs=[
        #         RequestInput(
        #             name='args',
        #             shape=[1],
        #             datatype='BYTES',
        #             parameters=None,
        #             data=TensorData(
        #                 __root__=['this is a test']
        #             )
        #         )
        #     ]
        #     outputs=None

        # TODO: convert and validate?
        kwargs = HuggingfaceRequestCodec.decode_request(payload)
        args = kwargs.pop("args", [])
        # print("runtime huggingface runtime predict kwargs:", kwargs)
        # runtime huggingface runtime predict kwargs: {}
        # print("runtime huggingface runtime predict args:", args)
        # runtime huggingface runtime predict args: ['this is a test']

        array_inputs = kwargs.pop("array_inputs", [])
        if array_inputs:
            args = [list(array_inputs)] + args
        prediction = self._model(*args, **kwargs)

        return self.encode_response(
            payload=prediction, default_codec=HuggingfaceRequestCodec
        )

    async def unload(self) -> bool:
        # TODO: Free up Tensorflow's GPU memory
        is_torch = self._model.framework == "pt"
        if not is_torch:
            return True

        uses_gpu = torch.cuda.is_available() and self._model.device != -1
        if not uses_gpu:
            # Nothing to free
            return True

        # Free up Torch's GPU memory
        torch.cuda.empty_cache()
        return True

    def _merge_metadata(self) -> None:
        meta = METADATA.get(self.hf_settings.task)
        if meta:
            self.inputs += meta.get("inputs", [])  # type: ignore
            self.outputs += meta.get("outputs", [])  # type: ignore
