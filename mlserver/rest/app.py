from typing import Callable
from fastapi import FastAPI
from fastapi.responses import Response as FastAPIResponse
from fastapi.routing import APIRoute as FastAPIRoute
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

from starlette_exporter import PrometheusMiddleware

from .endpoints import Endpoints, ModelRepositoryEndpoints
from .requests import Request
from .responses import Response
from .errors import _EXCEPTION_HANDLERS

from ..settings import Settings
from ..handlers import DataPlane, ModelRepositoryHandlers
from ..tracing import get_tracer_provider


class APIRoute(FastAPIRoute):
    """
    Custom route to use our own Request handler.
    """

    def __init__(
        self,
        *args,
        response_model_exclude_unset=True,
        response_model_exclude_none=True,
        response_class=Response,
        **kwargs
    ):
        super().__init__(
            *args,
            response_model_exclude_unset=response_model_exclude_unset,
            response_model_exclude_none=response_model_exclude_none,
            response_class=Response,
            **kwargs
        )

    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> FastAPIResponse:
            # print("resr app APIRoute request.scope:", request.scope)
            # resr app APIRoute request.scope:
            # {
            #     'type': 'http',
            #     'asgi': {
            #         'version': '3.0',
            #         'spec_version': '2.3'
            #     },
            #     'http_version': '1.1',
            #     'server': ('127.0.0.1', 8080),
            #     'client': ('127.0.0.1', 56818),
            #     'scheme': 'http',
            #     'method': 'POST',
            #     'root_path': '',
            #     'path': '/v2/models/mnist-svm/versions/v0.1.0/infer',
            #     'raw_path': b'/v2/models/mnist-svm/versions/v0.1.0/infer',
            #     'query_string': b'',
            #     'headers': [
            #         (b'host', b'localhost:8080'),
            #         (b'user-agent', b'python-requests/2.31.0'),
            #         (b'accept-encoding', b'gzip, deflate, br'),
            #         (b'accept', b'*/*'),
            #         (b'connection', b'keep-alive'),
            #         (b'content-length', b'428'),
            #         (b'content-type', b'application/json')
            #     ],
            #     'state': {},
            #     'app': <fastapi.applications.FastAPI object at 0x75fa294a0bb0>,
            #     'starlette.exception_handlers': (
            #         {
            #             <class 'starlette.exceptions.HTTPException'>: <function http_exception_handler at 0x75fa3404d5a0>,
            #             <class 'starlette.exceptions.WebSocketException'>: <bound method ExceptionMiddleware.websocket_exception of <starlette.middleware.exceptions.ExceptionMiddleware object at 0x75f9f45d9930>>,
            #             <class 'mlserver.errors.MLServerError'>: <function handle_mlserver_error at 0x75fa2b534160>,
            #             <class 'fastapi.exceptions.RequestValidationError'>: <function request_validation_exception_handler at 0x75fa3404d6c0>,
            #             <class 'fastapi.exceptions.WebSocketRequestValidationError'>: <function websocket_request_validation_exception_handler at 0x75fa3404d750>},
            #             {}
            #     ),
            #     'router': <fastapi.routing.APIRouter object at 0x75fa294a1030>,
            #     'endpoint': <bound method Endpoints.infer of <mlserver.rest.endpoints.Endpoints object at 0x75fa3576faf0>>,
            #     'path_params': {
            #         'model_name': 'mnist-svm',
            #         'model_version': 'v0.1.0'
            #     },
            #     'route': APIRoute(
            #         path='/v2/models/{model_name}/versions/{model_version}/infer',
            #         name='infer',
            #         methods=['POST']
            #     )
            # }
            ################################################
            # resr app APIRoute request.scope:
            # {
            #     'type': 'http',
            #     'asgi': {
            #         'version': '3.0',
            #         'spec_version': '2.3'
            #     },
            #     'http_version': '1.1',
            #     'server': ('127.0.0.1', 8080),
            #     'client': ('127.0.0.1', 51594),
            #     'scheme': 'http',
            #     'method': 'POST',
            #     'root_path': '',
            #     'path': '/v2/models/transformer/infer',
            #     'raw_path': b'/v2/models/transformer/infer',
            #     'query_string': b'',
            #     'headers': [
            #         (b'host', b'localhost:8080'),
            #         (b'user-agent', b'python-requests/2.31.0'),
            #         (b'accept-encoding', b'gzip, deflate, br'),
            #         (b'accept', b'*/*'),
            #         (b'connection', b'keep-alive'),
            #         (b'content-length', b'93'),
            #         (b'content-type', b'application/json')
            #     ],
            #     'state': {},
            #     'app': <fastapi.applications.FastAPI object at 0x70d60e159510>,
            #     'starlette.exception_handlers': (
            #         {
            #             <class 'starlette.exceptions.HTTPException'>: <function http_exception_handler at 0x70d620081900>,
            #             <class 'starlette.exceptions.WebSocketException'>: <bound method ExceptionMiddleware.websocket_exception of <starlette.middleware.exceptions.ExceptionMiddleware object at 0x70d4f9cbbd60>>,
            #             <class 'mlserver.errors.MLServerError'>: <function handle_mlserver_error at 0x70d60e496170>,
            #             <class 'fastapi.exceptions.RequestValidationError'>: <function request_validation_exception_handler at 0x70d6200827a0>,
            #             <class 'fastapi.exceptions.WebSocketRequestValidationError'>: <function websocket_request_validation_exception_handler at 0x70d620082830>},
            #             {}
            #     ),
            #     'router': <fastapi.routing.APIRouter object at 0x70d60e15b820>,
            #     'endpoint': <bound method Endpoints.infer of <mlserver.rest.endpoints.Endpoints object at 0x70d61f5a0820>>,
            #     'path_params': {'model_name': 'transformer'},
            #     'route': APIRoute(
            #         path='/v2/models/{model_name}/infer',
            #         name='infer',
            #         methods=['POST']
            #     )
            # }

            # print("resr app APIRoute request.app:", request.app)
            # resr app APIRoute request.app: <fastapi.applications.FastAPI object at 0x75fa294a0bb0>
            ################################################
            # resr app APIRoute request.app: <fastapi.applications.FastAPI object at 0x70d60e159510>

            # print("resr app APIRoute request.url:", request.url)
            # resr app APIRoute request.url: http://localhost:8080/v2/models/mnist-svm/versions/v0.1.0/infer
            ################################################
            # resr app APIRoute request.url: http://localhost:8080/v2/models/transformer/infer

            # print("resr app APIRoute request.base_url:", request.base_url)
            # resr app APIRoute request.base_url: http://localhost:8080/
            ################################################
            # resr app APIRoute request.base_url: http://localhost:8080/

            # print("resr app APIRoute request.headers:", request.headers)
            # resr app APIRoute request.headers:
            # Headers(
            #     {
            #         'host': 'localhost:8080',
            #         'user-agent': 'python-requests/2.31.0',
            #         'accept-encoding': 'gzip, deflate, br',
            #         'accept': '*/*',
            #         'connection': 'keep-alive',
            #         'content-length': '428',
            #         'content-type': 'application/json'
            #     }
            # )
            ################################################
            # resr app APIRoute request.headers:
            # Headers(
            #     {
            #         'host': 'localhost:8080',
            #         'user-agent': 'python-requests/2.31.0',
            #         'accept-encoding': 'gzip, deflate, br',
            #         'accept': '*/*',
            #         'connection': 'keep-alive',
            #         'content-length': '93',
            #         'content-type': 'application/json'
            #     }
            # )

            # print("resr app APIRoute request.query_params:", request.query_params)
            # resr app APIRoute request.query_params:
            ################################################
            # resr app APIRoute request.query_params:

            # print("resr app APIRoute request.path_params:", request.path_params)
            # resr app APIRoute request.path_params: {'model_name': 'mnist-svm', 'model_version': 'v0.1.0'}
            ################################################
            # resr app APIRoute request.path_params: {'model_name': 'transformer'}

            # print("resr app APIRoute request.cookies:", request.cookies)
            # resr app APIRoute request.cookies: {}
            ################################################
            # resr app APIRoute request.cookies: {}

            # print("resr app APIRoute request.client:", request.client)
            # resr app APIRoute request.client: Address(host='127.0.0.1', port=56818)
            ################################################
            # resr app APIRoute request.client: Address(host='127.0.0.1', port=51594)

            # print("resr app APIRoute request.session:", request.session)
            # print("resr app APIRoute request.auth:", request.auth)
            # print("resr app APIRoute request.user:", request.user)

            # print("resr app APIRoute request.state:", request.state)
            # resr app APIRoute request.state: <starlette.datastructures.State object at 0x75f9f45da9b0>
            ################################################
            # resr app APIRoute request.state: <starlette.datastructures.State object at 0x70d4f9cba950>

            # print("resr app APIRoute request.method:", request.method)
            # resr app APIRoute request.method: POST
            ################################################
            # resr app APIRoute request.method: POST

            # print("resr app APIRoute request.receive:", request.receive)
            # resr app APIRoute request.receive: <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.h11_impl.RequestResponseCycle object at 0x75f9f45da260>>
            ################################################
            # resr app APIRoute request.receive: <bound method RequestResponseCycle.receive of <uvicorn.protocols.http.h11_impl.RequestResponseCycle object at 0x70d4f9cb8820>>

            # print("resr app APIRoute request.body:", await request.body())
            # resr app APIRoute request.body:
            # b'{
            #     "inputs": [
            #         {
            #             "name": "predict",
            #             "shape": [1, 64],
            #             "datatype": "FP32",
            #             "data": [
            #                 [0.0, 0.0, 1.0, 11.0, 14.0, 15.0, 3.0, 0.0, 0.0, 1.0, 13.0, 16.0, 12.0, 16.0, 8.0, 0.0, 0.0, 8.0, 16.0, 4.0, 6.0, 16.0, 5.0, 0.0, 0.0, 5.0, 15.0, 11.0, 13.0, 14.0, 0.0, 0.0, 0.0, 0.0, 2.0, 12.0, 16.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 16.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 16.0, 16.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 11.0, 13.0, 12.0, 1.0, 0.0]
            #             ]
            #         }
            #     ]
            # }'
            ################################################
            # resr app APIRoute request.body:
            # b'{
            #     "inputs": [
            #         {
            #             "name": "args",
            #             "shape": [1],
            #             "datatype": "BYTES",
            #             "data": ["this is a test"]
            #         }
            #     ]
            # }'

            # print("resr app APIRoute request.json:", await request.json())
            # resr app APIRoute request.json:
            # {
            #     'inputs': [
            #         {
            #             'name': 'predict',
            #             'shape': [1, 64],
            #             'datatype': 'FP32',
            #             'data': [
            #                 [0.0, 0.0, 1.0, 11.0, 14.0, 15.0, 3.0, 0.0, 0.0, 1.0, 13.0, 16.0, 12.0, 16.0, 8.0, 0.0, 0.0, 8.0, 16.0, 4.0, 6.0, 16.0, 5.0, 0.0, 0.0, 5.0, 15.0, 11.0, 13.0, 14.0, 0.0, 0.0, 0.0, 0.0, 2.0, 12.0, 16.0, 13.0, 0.0, 0.0, 0.0, 0.0, 0.0, 13.0, 16.0, 16.0, 6.0, 0.0, 0.0, 0.0, 0.0, 16.0, 16.0, 16.0, 7.0, 0.0, 0.0, 0.0, 0.0, 11.0, 13.0, 12.0, 1.0, 0.0]
            #             ]
            #         }
            #     ]
            # }
            ################################################
            # resr app APIRoute request.json:
            # {
            #     'inputs': [
            #         {
            #             'name': 'args',
            #             'shape': [1],
            #             'datatype': 'BYTES',
            #             'data': ['this is a test']
            #         }
            #     ]
            # }

            request = Request(request.scope, request.receive)
            return await original_route_handler(request)

        return custom_route_handler


def create_app(
    settings: Settings,
    data_plane: DataPlane,
    model_repository_handlers: ModelRepositoryHandlers,
) -> FastAPI:
    endpoints = Endpoints(data_plane)
    model_repository_endpoints = ModelRepositoryEndpoints(model_repository_handlers)

    routes = [
        # Model ready
        APIRoute(
            "/v2/models/{model_name}/ready",
            endpoints.model_ready,
        ),
        APIRoute(
            "/v2/models/{model_name}/versions/{model_version}/ready",
            endpoints.model_ready,
        ),
        # Model infer
        APIRoute(
            "/v2/models/{model_name}/infer",
            endpoints.infer,
            methods=["POST"],
        ),
        APIRoute(
            "/v2/models/{model_name}/versions/{model_version}/infer",
            endpoints.infer,
            methods=["POST"],
        ),
        # Model metadata
        APIRoute(
            "/v2/models/{model_name}",
            endpoints.model_metadata,
        ),
        APIRoute(
            "/v2/models/{model_name}/versions/{model_version}",
            endpoints.model_metadata,
        ),
        # Model docs
        APIRoute(
            "/v2/models/{model_name}/docs/dataplane.json",
            endpoints.model_openapi,
        ),
        APIRoute(
            "/v2/models/{model_name}/versions/{model_version}/docs/dataplane.json",
            endpoints.model_openapi,
        ),
        APIRoute(
            "/v2/models/{model_name}/docs",
            endpoints.model_docs,
        ),
        APIRoute(
            "/v2/models/{model_name}/versions/{model_version}/docs",
            endpoints.model_docs,
        ),
        # Liveness and readiness
        APIRoute("/v2/health/live", endpoints.live),
        APIRoute("/v2/health/ready", endpoints.ready),
        # Server docs
        APIRoute(
            "/v2/docs/dataplane.json",
            endpoints.openapi,
        ),
        APIRoute(
            "/v2/docs",
            endpoints.docs,
        ),
        # Server metadata
        APIRoute(
            "/v2",
            endpoints.metadata,
        ),
    ]

    routes += [
        # Model Repository API
        APIRoute(
            "/v2/repository/index",
            model_repository_endpoints.index,
            methods=["POST"],
        ),
        APIRoute(
            "/v2/repository/models/{model_name}/load",
            model_repository_endpoints.load,
            methods=["POST"],
        ),
        APIRoute(
            "/v2/repository/models/{model_name}/unload",
            model_repository_endpoints.unload,
            methods=["POST"],
        ),
    ]

    app = FastAPI(
        debug=settings.debug,
        routes=routes,  # type: ignore
        default_response_class=Response,
        exception_handlers=_EXCEPTION_HANDLERS,  # type: ignore
        docs_url=None,
        redoc_url=None,
    )

    if settings.tracing_server:
        tracer_provider = get_tracer_provider(settings)
        excluded_urls = ",".join(
            [
                "/v2/health/live",
                "/v2/health/ready",
            ]
        )

        FastAPIInstrumentor.instrument_app(
            app,
            tracer_provider=tracer_provider,
            excluded_urls=excluded_urls,
        )

    app.router.route_class = APIRoute
    app.add_middleware(GZipMiddleware)
    if settings.cors_settings is not None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_settings.allow_origins,
            allow_origin_regex=settings.cors_settings.allow_origin_regex,
            allow_credentials=settings.cors_settings.allow_credentials,
            allow_methods=settings.cors_settings.allow_methods,
            allow_headers=settings.cors_settings.allow_headers,
            max_age=settings.cors_settings.max_age,
        )

    if settings.metrics_endpoint:
        app.add_middleware(
            PrometheusMiddleware,
            app_name="mlserver",
            prefix=settings.metrics_rest_server_prefix,
            # TODO: Should we also exclude model's health endpoints?
            skip_paths=[
                settings.metrics_endpoint,
                "/v2/health/live",
                "/v2/health/ready",
            ],
        )

    return app
