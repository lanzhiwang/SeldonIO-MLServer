import sys
import os
import json
import importlib
import inspect

from typing import Any, Dict, List, Optional, Type, Union, no_type_check, TYPE_CHECKING
from pydantic import PyObject, Extra, Field, BaseSettings as _BaseSettings
from contextlib import contextmanager

from .version import __version__
from .types import MetadataTensor

ENV_FILE_SETTINGS = ".env"
ENV_PREFIX_SETTINGS = "MLSERVER_"
ENV_PREFIX_MODEL_SETTINGS = "MLSERVER_MODEL_"

DEFAULT_PARALLEL_WORKERS = 1

DEFAULT_ENVIRONMENTS_DIR = os.path.join(os.getcwd(), ".envs")
DEFAULT_METRICS_DIR = os.path.join(os.getcwd(), ".metrics")

if TYPE_CHECKING:
    from ..model import MLModel


@contextmanager
def _extra_sys_path(extra_path: str):
    sys.path.insert(0, extra_path)

    yield

    sys.path.remove(extra_path)


def _get_import_path(klass: Type):
    return f"{klass.__module__}.{klass.__name__}"


def _reload_module(import_path: str):
    if not import_path:
        return

    module_path, _, _ = import_path.rpartition(".")
    module = importlib.import_module(module_path)
    importlib.reload(module)


class BaseSettings(_BaseSettings):
    @no_type_check
    def __setattr__(self, name, value):
        """
        Patch __setattr__ to be able to use property setters.
        From:
            https://github.com/pydantic/pydantic/issues/1577#issuecomment-790506164
        """
        try:
            super().__setattr__(name, value)
        except ValueError as e:
            setters = inspect.getmembers(
                self.__class__,
                predicate=lambda x: isinstance(x, property) and x.fset is not None,
            )
            for setter_name, func in setters:
                if setter_name == name:
                    object.__setattr__(self, name, value)
                    break
            else:
                raise e

    def dict(self, by_alias=True, exclude_unset=True, exclude_none=True, **kwargs):
        """
        Ensure that aliases are used, and that unset / none fields are ignored.
        """
        return super().dict(
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            **kwargs,
        )

    def json(self, by_alias=True, exclude_unset=True, exclude_none=True, **kwargs):
        """
        Ensure that aliases are used, and that unset / none fields are ignored.
        """
        return super().json(
            by_alias=by_alias,
            exclude_unset=exclude_unset,
            exclude_none=exclude_none,
            **kwargs,
        )


class CORSSettings(BaseSettings):
    class Config:
        env_file = ENV_FILE_SETTINGS
        env_prefix = ENV_PREFIX_SETTINGS

    allow_origins: Optional[List[str]] = []
    """
    A list of origins that should be permitted to make
    cross-origin requests. E.g. ['https://example.org', 'https://www.example.org'].
    You can use ['*'] to allow any origin
    """

    allow_origin_regex: Optional[str] = None
    """
    A regex string to match against origins that
    should be permitted to make cross-origin requests.
    e.g. 'https:\\/\\/.*\\.example\\.org'
    """

    allow_credentials: Optional[bool] = False
    """Indicate that cookies should be supported for cross-origin requests"""

    allow_methods: Optional[List[str]] = ["GET"]
    """A list of HTTP methods that should be allowed for cross-origin requests"""

    allow_headers: Optional[List[str]] = []
    """A list of HTTP request headers that should be supported for
    cross-origin requests"""

    expose_headers: Optional[List[str]] = []
    """Indicate any response headers that should be made accessible to the browser"""

    max_age: Optional[int] = 600
    """Sets a maximum time in seconds for browsers to cache CORS responses"""


class Settings(BaseSettings):
    class Config:
        env_file = ENV_FILE_SETTINGS
        env_prefix = ENV_PREFIX_SETTINGS

    debug: bool = True

    parallel_workers: int = DEFAULT_PARALLEL_WORKERS
    """When parallel inference is enabled, number of workers to run inference
    across."""

    parallel_workers_timeout: int = 5
    """Grace timeout to wait until the workers shut down when stopping MLServer."""

    environments_dir: str = DEFAULT_ENVIRONMENTS_DIR
    """
    Directory used to store custom environments.
    By default, the `.envs` folder of the current working directory will be
    used.
    """

    # Custom model repository class implementation
    model_repository_implementation: Optional[PyObject] = None
    """*Python path* to the inference runtime to model repository (e.g.
    ``mlserver.repository.repository.SchemalessModelRepository``)."""

    # Model repository settings
    model_repository_root: str = "."
    """Root of the model repository, where we will search for models."""

    # Model Repository parameters are meant to be set directly by the MLServer runtime.
    model_repository_implementation_args: dict = {}
    """Extra parameters for model repository."""

    load_models_at_startup: bool = True
    """Flag to load all available models automatically at startup."""

    # Server metadata
    server_name: str = "mlserver"
    """Name of the server."""

    server_version: str = __version__
    """Version of the server."""

    extensions: List[str] = []
    """Server extensions loaded."""

    # HTTP Server settings
    host: str = "0.0.0.0"
    """Host where to listen for connections."""

    http_port: int = 8080
    """Port where to listen for HTTP / REST connections."""

    root_path: str = ""
    """Set the ASGI root_path for applications submounted below a given URL path."""

    grpc_port: int = 8081
    """Port where to listen for gRPC connections."""

    grpc_max_message_length: Optional[int] = None
    """Maximum length (i.e. size) of gRPC payloads."""

    # CORS settings
    cors_settings: Optional[CORSSettings] = None

    # Metrics settings
    metrics_endpoint: Optional[str] = "/metrics"
    """
    Endpoint used to expose Prometheus metrics. Alternatively, can be set to
    `None` to disable it.
    """

    metrics_port: int = 8082
    """
    Port used to expose metrics endpoint.
    """

    metrics_rest_server_prefix: str = "rest_server"
    """
    Metrics rest server string prefix to be exported.
    """

    metrics_dir: str = DEFAULT_METRICS_DIR
    """
    Directory used to share metrics across parallel workers.
    Equivalent to the `PROMETHEUS_MULTIPROC_DIR` env var in
    `prometheus-client`.
    Note that this won't be used if the `parallel_workers` flag is disabled.
    By default, the `.metrics` folder of the current working directory will be
    used.
    """

    # Logging settings
    use_structured_logging: bool = False
    """Use JSON-formatted structured logging instead of default format."""
    logging_settings: Optional[Union[str, Dict]] = None
    """Path to logging config file or dictionary configuration."""

    # Kafka Server settings
    kafka_enabled: bool = False
    kafka_servers: str = "localhost:9092"
    kafka_topic_input: str = "mlserver-input"
    kafka_topic_output: str = "mlserver-output"

    # OpenTelemetry Tracing settings
    tracing_server: Optional[str] = None
    """Server name used to export OpenTelemetry tracing to collector service."""

    # Custom server settings
    _custom_rest_server_settings: Optional[dict] = None
    _custom_metrics_server_settings: Optional[dict] = None
    _custom_grpc_server_settings: Optional[dict] = None

    cache_enabled: bool = False
    """Enable caching for the model predictions."""

    cache_size: int = 100
    """Cache size to be used if caching is enabled."""


class ModelParameters(BaseSettings):
    """
    Parameters that apply only to a particular instance of a model.
    This can include things like model weights, or arbitrary ``extra``
    parameters particular to the underlying inference runtime.
    The main difference with respect to ``ModelSettings`` is that parameters
    can change on each instance (e.g. each version) of the model.
    """

    class Config:
        extra = Extra.allow
        env_file = ENV_FILE_SETTINGS
        env_prefix = ENV_PREFIX_MODEL_SETTINGS

    uri: Optional[str] = None
    """
    URI where the model artifacts can be found.
    This path must be either absolute or relative to where MLServer is running.
    """

    version: Optional[str] = None
    """Version of the model."""

    environment_tarball: Optional[str] = None
    """Path to the environment tarball which should be used to load this
    model."""

    format: Optional[str] = None
    """Format of the model (only available on certain runtimes)."""

    content_type: Optional[str] = None
    """Default content type to use for requests and responses."""

    extra: Optional[dict] = {}
    """Arbitrary settings, dependent on the inference runtime
    implementation."""


class ModelSettings(BaseSettings):
    class Config:
        env_file = ENV_FILE_SETTINGS
        env_prefix = ENV_PREFIX_MODEL_SETTINGS
        underscore_attrs_are_private = True

    # Source points to the file where model settings were loaded from
    _source: Optional[str] = None

    def __init__(self, *args, **kwargs):
        # Ensure we still support inline init, e.g.
        # ModelSettings(implementation=SumModel)
        implementation = kwargs.get("implementation", None)
        if inspect.isclass(implementation):
            kwargs["implementation"] = _get_import_path(implementation)

        super().__init__(*args, **kwargs)

    @classmethod
    def parse_file(cls, path: str) -> "ModelSettings":  # type: ignore
        # print('settings ModelSettings parse_file path:', path)
        # settings ModelSettings parse_file path: /workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models/model-settings.json

        with open(path, "r") as f:
            obj = json.load(f)
            # print('settings ModelSettings parse_file obj:', obj)
            # settings ModelSettings parse_file obj:
            # {
            #     'name': 'transformer',
            #     'implementation': 'mlserver_huggingface.HuggingFaceRuntime',
            #     'parameters': {
            #         'extra': {
            #             'task': 'text-generation',
            #             'pretrained_model': 'distilgpt2'
            #         }
            #     }
            # }

            obj["_source"] = path
            # print('settings ModelSettings parse_file obj:', obj)
            # settings ModelSettings parse_file obj:
            # {
            #     'name': 'transformer',
            #     'implementation': 'mlserver_huggingface.HuggingFaceRuntime',
            #     'parameters': {
            #         'extra': {
            #             'task': 'text-generation',
            #             'pretrained_model': 'distilgpt2'
            #         }
            #     },
            #     '_source': '/workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models/model-settings.json'
            # }

            return cls.parse_obj(obj)

    @classmethod
    def parse_obj(cls, obj: Any) -> "ModelSettings":
        # print('settings ModelSettings parse_obj obj:', obj)
        # settings ModelSettings parse_obj obj:
        # {
        #     'name': 'transformer',
        #     'implementation': 'mlserver_huggingface.HuggingFaceRuntime',
        #     'parameters': {
        #         'extra': {
        #             'task': 'text-generation',
        #             'pretrained_model': 'distilgpt2'
        #         }
        #     },
        #     '_source': '/workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models/model-settings.json'
        # }

        source = obj.pop("_source", None)
        model_settings = super().parse_obj(obj)
        # print('settings ModelSettings parse_obj model_settings:', model_settings)
        # settings ModelSettings parse_obj model_settings:
        #     name='transformer'
        #     platform=''
        #     versions=[]
        #     inputs=[]
        #     outputs=[]
        #     parallel_workers=None
        #     warm_workers=False
        #     max_batch_size=0
        #     max_batch_time=0.0
        #     implementation_='mlserver_huggingface.HuggingFaceRuntime'
        #     parameters=ModelParameters(
        #         uri=None,
        #         version=None,
        #         environment_tarball=None,
        #         format=None,
        #         content_type=None,
        #         extra={
        #             'task': 'text-generation',
        #             'pretrained_model': 'distilgpt2'
        #         }
        #     )
        #     cache_enabled=False

        if source:
            model_settings._source = source

        return model_settings


    @property
    def implementation(self) -> Type["MLModel"]:
        if not self._source:
            return PyObject.validate(self.implementation_)  # type: ignore

        model_folder = os.path.dirname(self._source)
        with _extra_sys_path(model_folder):
            _reload_module(self.implementation_)
            return PyObject.validate(self.implementation_)  # type: ignore

    @implementation.setter
    def implementation(self, value: Type["MLModel"]):
        self.implementation_ = _get_import_path(value)

    @property
    def version(self) -> Optional[str]:
        params = self.parameters
        if params is not None:
            return params.version
        return None

    name: str = ""
    """Name of the model."""

    # Model metadata
    platform: str = ""
    """Framework used to train and serialise the model (e.g. sklearn)."""

    versions: List[str] = []
    """Versions of dependencies used to train the model (e.g.
    sklearn/0.20.1)."""

    inputs: List[MetadataTensor] = []
    """Metadata about the inputs accepted by the model."""

    outputs: List[MetadataTensor] = []
    """Metadata about the outputs returned by the model."""

    # Parallel settings
    parallel_workers: Optional[int] = Field(
        None,
        deprecated=True,
        description=(
            "Use the `parallel_workers` field the server wide settings instead."
        ),
    )

    warm_workers: bool = Field(
        False,
        deprecated=True,
        description="Inference workers will now always be `warmed up` at start time.",
    )

    # Adaptive Batching settings (disabled by default)
    max_batch_size: int = 0
    """When adaptive batching is enabled, maximum number of requests to group
    together in a single batch."""

    max_batch_time: float = 0.0
    """When adaptive batching is enabled, maximum amount of time (in seconds)
    to wait for enough requests to build a full batch."""

    # Custom model class implementation
    # NOTE: The `implementation_` attr will only point to the string import.
    # The actual import will occur within the `implementation` property - think
    # of this as a lazy import.
    # You should always use `model_settings.implementation` and treat
    # `implementation_` as a private attr (due to Pydantic - we can't just
    # prefix the attr with `_`).
    implementation_: str = Field(
        alias="implementation", env="MLSERVER_MODEL_IMPLEMENTATION"
    )
    """*Python path* to the inference runtime to use to serve this model (e.g.
    ``mlserver_sklearn.SKLearnModel``)."""

    # Model parameters are meant to be set directly by the MLServer runtime.
    # However, it's also possible to override them manually.
    parameters: Optional[ModelParameters] = None
    """Extra parameters for each instance of this model."""

    cache_enabled: bool = False
    """Enable caching for a specific model. This parameter can be used to disable
    cache for a specific model, if the server level caching is enabled. If the
    server level caching is disabled, this parameter value will have no effect."""
