from fastapi import APIRouter, Depends
from pydantic.alias_generators import to_snake

# ?
import bia_shared_datamodels.bia_data_model as shared_data_models
from .models.repository import Repository


router = APIRouter()
models_public = [
    shared_data_models.Study,
    shared_data_models.ImageAnnotationDataset,
    shared_data_models.ExperimentalImagingDataset,
    shared_data_models.AnnotationFileReference,
    shared_data_models.FileReference,
]


def make_get_item(t):
    # variables are function-scoped => add wrapper to bind each value of t
    # https://eev.ee/blog/2011/04/24/gotcha-python-scoping-closures/

    # @TODO: nicer wrapper?
    async def get_item(
        uuid: shared_data_models.UUID, db: Repository = Depends()
    ) -> dict:
        return await db.get_doc(uuid, t)

    return get_item


for t in models_public:
    router.add_api_route(
        f"/{to_snake(t.__name__)}/{{uuid}}",
        response_model=t,
        operation_id=f"get{t.__name__}",
        summary=f"Get {t.__name__}",
        methods=["GET"],
        endpoint=make_get_item(t),
    )


@router.get("/other_resource_no_overwrite")
def not_overwritten(n: int) -> int:
    return n


# @router.get("/study")
# def yes_overwritten(n: int) -> int:
#    return n
