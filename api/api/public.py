from fastapi import APIRouter, Depends
from pydantic.alias_generators import to_snake

# ?
import bia_shared_datamodels.bia_data_model as shared_data_models
from .models.repository import Repository
from . import constants


router = APIRouter(
    prefix="/private",
    # dependencies=[Depends(get_current_user)], TODO
    tags=[constants.OPENAPI_TAG_PUBLIC],
)
models_public = [
    shared_data_models.Study,
    shared_data_models.FileReference,
    shared_data_models.ImageRepresentation,
    shared_data_models.ExperimentalImagingDataset,
    shared_data_models.Specimen,
    shared_data_models.ExperimentallyCapturedImage,
    shared_data_models.ImageAcquisition,
    shared_data_models.SpecimenImagingPrepartionProtocol,
    shared_data_models.SpecimenGrowthProtocol,
    shared_data_models.BioSample,
    shared_data_models.ImageAnnotationDataset,
    shared_data_models.AnnotationFileReference,
    shared_data_models.DerivedImage,
    shared_data_models.AnnotationMethod,
]


def make_get_item(t):
    # variables are function-scoped => add wrapper to bind each value of t
    # https://eev.ee/blog/2011/04/24/gotcha-python-scoping-closures/

    # @TODO: nicer wrapper?
    async def get_item(uuid: shared_data_models.UUID, db: Repository = Depends()) -> t:
        return await db.get_doc(uuid, t)

    return get_item


def make_router() -> APIRouter:
    for t in models_public:
        router.add_api_route(
            f"/{to_snake(t.__name__)}/{{uuid}}",
            response_model=t,
            operation_id=f"get{t.__name__}",
            summary=f"Get {t.__name__}",
            methods=["GET"],
            endpoint=make_get_item(t),
        )

    return router


@router.get("/placeholder")
def example_custom_handler():
    pass
