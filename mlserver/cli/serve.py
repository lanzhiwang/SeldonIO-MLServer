import os
import sys

from typing import Optional, List, Tuple, Union

from mlserver.repository.factory import ModelRepositoryFactory

from ..settings import Settings, ModelSettings

DEFAULT_SETTINGS_FILENAME = "settings.json"


async def load_settings(
    folder: Optional[str] = None,
) -> Tuple[Settings, List[ModelSettings]]:
    """
    Load server and model settings.
    """
    # NOTE: Insert current directory and model folder into syspath to load
    # specified model.
    sys.path.insert(0, ".")

    if folder:
        sys.path.insert(0, folder)

    settings = None
    if _path_exists(folder, DEFAULT_SETTINGS_FILENAME):
        settings_path = os.path.join(folder, DEFAULT_SETTINGS_FILENAME)  # type: ignore
        print("cli serve load_settings settings_path:", settings_path)
        # cli serve load_settings settings_path: ./example/02-Serving-HuggingFace-models/settings.json
        settings = Settings.parse_file(settings_path)
    else:
        settings = Settings()
    print("cli serve load_settings settings:", settings)
    # cli serve load_settings settings:
    #     debug=True
    #     parallel_workers=1
    #     parallel_workers_timeout=5
    #     environments_dir='/workspaces/SeldonIO-MLServer/.envs'
    #     model_repository_implementation=None
    #     model_repository_root='.'
    #     model_repository_implementation_args={}
    #     load_models_at_startup=True
    #     server_name='mlserver'
    #     server_version='1.5.0'
    #     extensions=[]
    #     host='0.0.0.0'
    #     http_port=8080
    #     root_path=''
    #     grpc_port=8081
    #     grpc_max_message_length=None
    #     cors_settings=None
    #     metrics_endpoint='/metrics'
    #     metrics_port=8082
    #     metrics_rest_server_prefix='rest_server'
    #     metrics_dir='/workspaces/SeldonIO-MLServer/.metrics'
    #     use_structured_logging=False
    #     logging_settings=None
    #     kafka_enabled=False
    #     kafka_servers='localhost:9092'
    #     kafka_topic_input='mlserver-input'
    #     kafka_topic_output='mlserver-output'
    #     tracing_server=None
    #     cache_enabled=False
    #     cache_size=100

    if folder is not None:
        settings.model_repository_root = folder
    print("cli serve load_settings settings:", settings)
    # cli serve load_settings settings:
    #     debug=True
    #     parallel_workers=1
    #     parallel_workers_timeout=5
    #     environments_dir='/workspaces/SeldonIO-MLServer/.envs'
    #     model_repository_implementation=None
    #     model_repository_root='./example/02-Serving-HuggingFace-models/'
    #     model_repository_implementation_args={}
    #     load_models_at_startup=True
    #     server_name='mlserver'
    #     server_version='1.5.0'
    #     extensions=[]
    #     host='0.0.0.0'
    #     http_port=8080
    #     root_path=''
    #     grpc_port=8081
    #     grpc_max_message_length=None
    #     cors_settings=None
    #     metrics_endpoint='/metrics'
    #     metrics_port=8082
    #     metrics_rest_server_prefix='rest_server'
    #     metrics_dir='/workspaces/SeldonIO-MLServer/.metrics'
    #     use_structured_logging=False
    #     logging_settings=None
    #     kafka_enabled=False
    #     kafka_servers='localhost:9092'
    #     kafka_topic_input='mlserver-input'
    #     kafka_topic_output='mlserver-output'
    #     tracing_server=None
    #     cache_enabled=False
    #     cache_size=100

    models_settings = []
    if settings.load_models_at_startup:
        repository = ModelRepositoryFactory.resolve_model_repository(settings)
        models_settings = await repository.list()
    print("cli serve load_settings models_settings:", models_settings)
    # cli serve load_settings models_settings:
    # [
    #     ModelSettings(
    #         name='transformer',
    #         platform='',
    #         versions=[],
    #         inputs=[],
    #         outputs=[],
    #         parallel_workers=None,
    #         warm_workers=False,
    #         max_batch_size=0,
    #         max_batch_time=0.0,
    #         implementation_='mlserver_huggingface.HuggingFaceRuntime',
    #         parameters=ModelParameters(
    #             uri='/workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models',
    #             version=None,
    #             environment_tarball=None,
    #             format=None,
    #             content_type=None,
    #             extra={
    #                 'task': 'text-generation',
    #                 'pretrained_model': 'distilgpt2'
    #             }
    #         ),
    #         cache_enabled=False
    #     )
    # ]

    return settings, models_settings


def _path_exists(folder: Union[str, None], file: str) -> bool:
    if folder is None:
        return False

    file_path = os.path.join(folder, file)
    return os.path.isfile(file_path)
