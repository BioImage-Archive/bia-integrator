from fastapi import APIRouter
from pydantic.alias_generators import to_snake

import bia_shared_datamodels.bia_data_model as shared_data_models
from models.repository import Repository
from api import constants
from api import auth
from fastapi import APIRouter, Depends, status
from typing import List, Type

router = APIRouter(
    prefix="/private",
    dependencies=[Depends(auth.get_current_user)],
    tags=[constants.OPENAPI_TAG_PRIVATE],
)
models_private: List[shared_data_models.DocumentMixin] = [
    shared_data_models.Study,
    shared_data_models.FileReference,
    shared_data_models.ImageRepresentation,
    shared_data_models.ExperimentalImagingDataset,
    shared_data_models.Specimen,
    shared_data_models.ExperimentallyCapturedImage,
    shared_data_models.ImageAcquisition,
    shared_data_models.SpecimenImagingPreparationProtocol,
    shared_data_models.SpecimenGrowthProtocol,
    shared_data_models.BioSample,
    shared_data_models.ImageAnnotationDataset,
    shared_data_models.AnnotationFileReference,
    shared_data_models.DerivedImage,
    shared_data_models.AnnotationMethod,
]


def make_post_item(t: Type[shared_data_models.DocumentMixin]):
    async def post_item(doc: t, db: Repository = Depends()) -> None:
        await db.persist_doc(doc)

    return post_item


def make_router() -> APIRouter:
    for t in models_private:
        router.add_api_route(
            "/" + to_snake(t.__name__),
            operation_id=f"post{t.__name__}",
            summary=f"Create {t.__name__}",
            methods=["POST"],
            endpoint=make_post_item(t),
            status_code=status.HTTP_201_CREATED,
        )

    return router
