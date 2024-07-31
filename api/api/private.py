from fastapi import APIRouter
from pydantic.alias_generators import to_snake

# ?
import bia_shared_datamodels.bia_data_model as shared_data_models
from .models.repository import Repository
from . import constants
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/private",
    # dependencies=[Depends(get_current_user)], TODO
    tags=[constants.OPENAPI_TAG_PRIVATE],
)
models_private = [
    shared_data_models.Study,
    shared_data_models.ImageAnnotationDataset,
    shared_data_models.ExperimentalImagingDataset,
    shared_data_models.AnnotationFileReference,
    shared_data_models.FileReference,
]


def make_post_item(t):
    async def post_item(doc: t, db: Repository = Depends()) -> None:
        await db.persist_doc(doc)

    return post_item


for t in models_private:
    router.add_api_route(
        "/" + to_snake(t.__name__),
        operation_id=f"post{t.__name__}",
        summary=f"Create {t.__name__}",
        methods=["POST"],
        endpoint=make_post_item(t),
    )
