from .repository import ModelRepository, SchemalessModelRepository
from ..settings import Settings
from pydantic import PyObject


class ModelRepositoryFactory:
    @staticmethod
    def resolve_model_repository(settings: Settings) -> ModelRepository:
        model_repository_implementation: PyObject = SchemalessModelRepository

        result: ModelRepository
        # model_repository_implementation=None
        if settings.model_repository_implementation:
            model_repository_implementation = settings.model_repository_implementation

        # model_repository_root='./example/02-Serving-HuggingFace-models/'
        result = model_repository_implementation(
            root=settings.model_repository_root,
            **settings.model_repository_implementation_args,
        )

        return result
