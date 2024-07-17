import os

from ..settings import ModelParameters, ModelSettings
from ..logging import logger


def load_model_settings(model_settings_path: str) -> ModelSettings:
    # print("repository load load_model_settings model_settings_path:", model_settings_path)
    # repository load load_model_settings model_settings_path: /workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models/model-settings.json

    model_settings = ModelSettings.parse_file(model_settings_path)
    # print("repository load load_model_settings model_settings:", model_settings)
    # repository load load_model_settings model_settings:
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

    # If name not present, default to folder name
    model_settings_folder = os.path.dirname(model_settings_path)
    # print("repository load load_model_settings model_settings_folder:", model_settings_folder)
    # repository load load_model_settings model_settings_folder: /workspaces/SeldonIO-MLServer/example/02-Serving-HuggingFace-models

    folder_name = os.path.basename(model_settings_folder)
    # print("repository load load_model_settings folder_name:", folder_name)
    # repository load load_model_settings folder_name: 02-Serving-HuggingFace-models

    if model_settings.name:
        if not _folder_matches(folder_name, model_settings):
            # Raise warning if name is different than folder's name
            logger.warning(
                f"Model name '{model_settings.name}' is different than "
                f"model's folder name '{folder_name}'."
            )
    else:
        model_settings.name = folder_name

    if not model_settings.parameters:
        model_settings.parameters = ModelParameters()

    if not model_settings.parameters.uri:
        # If not specified, default to its own folder
        default_model_uri = os.path.dirname(model_settings_path)
        model_settings.parameters.uri = default_model_uri

    return model_settings


def _folder_matches(folder_name: str, model_settings: ModelSettings) -> bool:
    if model_settings.name == folder_name:
        return True

    # To be compatible with Triton, check whether the folder name matches
    # with the model's version
    if model_settings.parameters and model_settings.parameters.version:
        model_version = model_settings.parameters.version
        if model_version == folder_name:
            return True

    return False
