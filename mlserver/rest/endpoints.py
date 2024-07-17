from fastapi.requests import Request
from fastapi.responses import Response, HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html

from typing import Optional

from ..types import (
    MetadataModelResponse,
    MetadataServerResponse,
    InferenceRequest,
    InferenceResponse,
    RepositoryIndexRequest,
    RepositoryIndexResponse,
)
from ..handlers import DataPlane, ModelRepositoryHandlers
from ..utils import insert_headers, extract_headers

from .openapi import get_openapi_schema, get_model_schema_uri, get_model_schema
from .utils import to_status_code


class Endpoints:
    """
    Implementation of REST endpoints.
    These take care of the REST/HTTP-specific things and then delegate the
    business logic to the internal handlers.
    """

    def __init__(self, data_plane: DataPlane):
        self._data_plane = data_plane

    async def live(self) -> Response:
        is_live = await self._data_plane.live()
        return Response(status_code=to_status_code(is_live))

    async def ready(self) -> Response:
        is_ready = await self._data_plane.ready()
        return Response(status_code=to_status_code(is_ready))

    async def openapi(self) -> dict:
        return get_openapi_schema()

    async def docs(self) -> HTMLResponse:
        openapi_url = "/v2/docs/dataplane.json"
        title = "MLServer API Docs"
        return get_swagger_ui_html(openapi_url=openapi_url, title=title)

    async def model_openapi(
        self, model_name: str, model_version: Optional[str] = None
    ) -> dict:
        # NOTE: Right now, we use the `model_metadata` method to check that the
        # model exists.
        # In the future, we will use this metadata to fill in more model
        # details in the schema (e.g. expected inputs, etc.).
        await self._data_plane.model_metadata(model_name, model_version)
        return get_model_schema(model_name, model_version)

    async def model_docs(
        self, model_name: str, model_version: Optional[str] = None
    ) -> HTMLResponse:
        # NOTE: Right now, we use the `model_metadata` method to check that the
        # model exists.
        # In the future, we will use this metadata to fill in more model
        # details in the schema (e.g. expected inputs, etc.).
        await self._data_plane.model_metadata(model_name, model_version)
        openapi_url = get_model_schema_uri(model_name, model_version)

        title = f"MLServer API Docs - {model_name}"
        if model_version:
            title = f"{title} ({model_version})"

        return get_swagger_ui_html(openapi_url=openapi_url, title=title)

    async def model_ready(
        self, model_name: str, model_version: Optional[str] = None
    ) -> Response:
        is_ready = await self._data_plane.model_ready(model_name, model_version)
        return Response(status_code=to_status_code(is_ready))

    async def metadata(self) -> MetadataServerResponse:
        return await self._data_plane.metadata()

    async def model_metadata(
        self, model_name: str, model_version: Optional[str] = None
    ) -> MetadataModelResponse:
        return await self._data_plane.model_metadata(model_name, model_version)

    async def infer(
        self,
        raw_request: Request,
        raw_response: Response,
        payload: InferenceRequest,
        model_name: str,
        model_version: Optional[str] = None,
    ) -> InferenceResponse:
        print("rest endpoint Endpoints infer raw_request:", raw_request)
        # rest endpoint Endpoints infer raw_request: <mlserver.rest.requests.Request object at 0x7fd4ad491630>
        print("rest endpoint Endpoints infer raw_response:", raw_response)
        # rest endpoint Endpoints infer raw_response: <starlette.responses.Response object at 0x7fd4ad4910f0>
        print("rest endpoint Endpoints infer payload:", payload)
        # rest endpoint Endpoints infer payload:
        #     id=None
        #     parameters=None
        #     inputs=[
        #         RequestInput(
        #             name='predict',
        #             shape=[1, 64],
        #             datatype='FP32',
        #             parameters=None,
        #             data=TensorData(
        #                 __root__=[
        #                     [0.0, 0.0, 1.0, 11.0, 14.0, 15.0, 3.0, 0.0, 0.0, 1.0, 13.0, 16.0, 12.0, 16.0, 8.0, 0.0, 0.0, 8.0, 16.0, 4.0, 6.0, 16.0, 5.0, 0.0, 0.0, 5.0, 15.0, 11.0, 13.0, 14.0, 0.0, 0.0, 0.0, 0.0, 2.0, 12.0, 16.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 16.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 16.0, 16.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 11.0, 13.0, 12.0, 1.0, 0.0]
        #                 ]
        #             )
        #         )
        #     ]
        #     outputs=None
        print("rest endpoint Endpoints infer model_name:", model_name)
        # rest endpoint Endpoints infer model_name: mnist-svm
        print("rest endpoint Endpoints infer model_version:", model_version)
        # rest endpoint Endpoints infer model_version: v0.1.0

        request_headers = dict(raw_request.headers)
        print("rest endpoint Endpoints infer request_headers:", request_headers)
        # rest endpoint Endpoints infer request_headers:
        # {
        #     'host': 'localhost:8080',
        #     'user-agent': 'python-requests/2.31.0',
        #     'accept-encoding': 'gzip, deflate, br',
        #     'accept': '*/*',
        #     'connection': 'keep-alive',
        #     'content-length': '428',
        #     'content-type': 'application/json'
        # }

        insert_headers(payload, request_headers)
        print("rest endpoint Endpoints infer request_headers:", request_headers)
        # rest endpoint Endpoints infer request_headers:
        # {
        #     'host': 'localhost:8080',
        #     'user-agent': 'python-requests/2.31.0',
        #     'accept-encoding': 'gzip, deflate, br',
        #     'accept': '*/*',
        #     'connection': 'keep-alive',
        #     'content-length': '428',
        #     'content-type': 'application/json'
        # }
        print("rest endpoint Endpoints infer payload:", payload)
        # rest endpoint Endpoints infer payload:
        #     id=None
        #     parameters=Parameters(
        #         content_type=None,
        #         headers={
        #             'host': 'localhost:8080',
        #             'user-agent': 'python-requests/2.31.0',
        #             'accept-encoding': 'gzip, deflate, br',
        #             'accept': '*/*',
        #             'connection': 'keep-alive',
        #             'content-length': '428',
        #             'content-type': 'application/json'
        #         }
        #     )
        #     inputs=[
        #         RequestInput(
        #             name='predict',
        #             shape=[1, 64],
        #             datatype='FP32',
        #             parameters=None,
        #             data=TensorData(
        #                 __root__=[
        #                     [0.0, 0.0, 1.0, 11.0, 14.0, 15.0, 3.0, 0.0, 0.0, 1.0, 13.0, 16.0, 12.0, 16.0, 8.0, 0.0, 0.0, 8.0, 16.0, 4.0, 6.0, 16.0, 5.0, 0.0, 0.0, 5.0, 15.0, 11.0, 13.0, 14.0, 0.0, 0.0, 0.0, 0.0, 2.0, 12.0, 16.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 16.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 16.0, 16.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 11.0, 13.0, 12.0, 1.0, 0.0]
        #                 ]
        #             )
        #         )
        #     ]
        #     outputs=None

        inference_response = await self._data_plane.infer(
            payload, model_name, model_version
        )
        print("rest endpoint Endpoints infer inference_response:", inference_response)
        # rest endpoint Endpoints infer inference_response:
        #     model_name='mnist-svm'
        #     model_version='v0.1.0'
        #     id='516e7dc1-b1c0-48e5-9a3e-d391e7657c68'
        #     parameters=Parameters(
        #         content_type=None,
        #         headers={
        #             'Ce-Specversion': '0.3',
        #             'Ce-Source': 'io.seldon.serving.deployment.mlserver',
        #             'Ce-Type': 'io.seldon.serving.inference.response',
        #             'Ce-Modelid': 'mnist-svm',
        #             'Ce-Inferenceservicename': 'mlserver',
        #             'Ce-Endpoint': 'mnist-svm',
        #             'Ce-Id': '516e7dc1-b1c0-48e5-9a3e-d391e7657c68',
        #             'Ce-Requestid': '516e7dc1-b1c0-48e5-9a3e-d391e7657c68'
        #         }
        #     )
        #     outputs=[
        #         ResponseOutput(
        #             name='predict',
        #             shape=[1, 1],
        #             datatype='INT64',
        #             parameters=Parameters(
        #                 content_type='np',
        #                 headers=None
        #             ),
        #             data=TensorData(
        #                 __root__=[8]
        #             )
        #         )
        #     ]

        response_headers = extract_headers(inference_response)
        print("rest endpoint Endpoints infer response_headers:", response_headers)
        # rest endpoint Endpoints infer response_headers:
        # {
        #     'Ce-Specversion': '0.3',
        #     'Ce-Source': 'io.seldon.serving.deployment.mlserver',
        #     'Ce-Type': 'io.seldon.serving.inference.response',
        #     'Ce-Modelid': 'mnist-svm',
        #     'Ce-Inferenceservicename': 'mlserver',
        #     'Ce-Endpoint': 'mnist-svm',
        #     'Ce-Id': '516e7dc1-b1c0-48e5-9a3e-d391e7657c68',
        #     'Ce-Requestid': '516e7dc1-b1c0-48e5-9a3e-d391e7657c68'
        # }

        if response_headers:
            raw_response.headers.update(response_headers)
        print("rest endpoint Endpoints infer raw_response:", raw_response)
        # rest endpoint Endpoints infer raw_response: <starlette.responses.Response object at 0x7fd4ad4910f0>

        print("rest endpoint Endpoints infer inference_response:", inference_response)
        # rest endpoint Endpoints infer inference_response: model_name='mnist-svm' model_version='v0.1.0' id='516e7dc1-b1c0-48e5-9a3e-d391e7657c68' parameters=Parameters(content_type=None, headers=None) outputs=[ResponseOutput(name='predict', shape=[1, 1], datatype='INT64', parameters=Parameters(content_type='np', headers=None), data=TensorData(__root__=[8]))]

        return inference_response


class ModelRepositoryEndpoints:
    def __init__(self, handlers: ModelRepositoryHandlers):
        self._handlers = handlers

    async def index(self, payload: RepositoryIndexRequest) -> RepositoryIndexResponse:
        return await self._handlers.index(payload)

    async def load(self, model_name: str) -> Response:
        loaded = await self._handlers.load(name=model_name)
        return Response(status_code=to_status_code(loaded))

    async def unload(self, model_name: str) -> Response:
        unloaded = await self._handlers.unload(name=model_name)
        return Response(status_code=to_status_code(unloaded))
