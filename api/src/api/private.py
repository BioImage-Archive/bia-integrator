from ..models import persistence as db_models
from ..models import repository  as repository
from ..models import api as api_models
from ..api import exceptions

from typing import List, Optional
from fastapi import APIRouter, status

router = APIRouter(prefix="/api/private")

@router.post("/study", status_code=status.HTTP_201_CREATED)
async def create_study(study: db_models.BIAStudy) -> Optional[db_models.BIAStudy]:
    if study.version != 0:
        raise exceptions.InvalidRequestException(f"Expecting all newly created objects to have version 0. Got {study.version}")
    
    await repository.persist_doc(study)
    study_created = await repository.find_study_by_uuid(study.uuid)
    
    return study_created

@router.patch("/study", status_code=status.HTTP_201_CREATED)
async def update_study(study: db_models.BIAStudy) -> Optional[db_models.BIAStudy]:
    await repository.update_doc(study)
    
    study_updated = await repository.find_study_by_uuid(study.uuid)
    return study_updated

@router.post("/studies/{study_uuid}/refresh_counts")
async def study_refresh_counts(study_uuid: str) -> Optional[db_models.BIAStudy]:
    """Recalculate and persist counts for other objects pointing to this study."""
    repository.refresh_counts(study_uuid)

    bia_study = repository.find_study_by_uuid(study_uuid)
    return bia_study

@router.post("/images", status_code=status.HTTP_201_CREATED)
async def create_images(study_images: List[db_models.BIAImage]) -> api_models.BulkOperationResponse:
    # no individual errors for this since images will generally be created with the same study
    insert_errors_by_uuid = {}
    image_studies_not_found = {
        study_image.study_uuid: None
        for study_image in study_images
    }
    for study_uuid in image_studies_not_found.keys():
        try:
            await repository.find_study_by_uuid(study_uuid)
        except exceptions.DocumentNotFound as e:
            image_studies_not_found[study_uuid] = e
    if any([v for v in image_studies_not_found if v is not None]):
        for study_image in study_images:
            image_error = image_studies_not_found[study_image.study_uuid]
            if image_error:
                insert_errors_by_uuid[study_image.uuid] = {
                    'errmsg': image_error.detail
                }

    insert_results = await repository.persist_docs(study_images, insert_errors_by_uuid=insert_errors_by_uuid)

    rsp = api_models.BulkOperationResponse(items=insert_results)

    return rsp

@router.patch("/images/single", status_code=status.HTTP_200_OK)
async def update_image(study_image: db_models.BIAImage) -> db_models.BIAImage:
    """Bulk update not available - update_many only has one filter for the entire update
    @TODO: Find common bulk update usecases and map them to mongo operations"""
    await repository.find_study_by_uuid(study_image.study_uuid)

    await repository.update_doc(study_image)
    image_updated = await repository.find_image_by_uuid(study_image.uuid)
    
    return image_updated

@router.post("/images/bulk")
async def create_images() -> None:
    """TODO: Maybe file-based async?"""
    raise Exception("Not implemented")

@router.post("/images/representations")
async def create_image_representations(representations : List[db_models.BIAImageRepresentation]) -> api_models.BulkOperationResponse:
    representations_images = {
        representation.image
        for representation in representations
    }
    for image_uuid in representations_images:
        await repository.find_image_by_uuid(image_uuid)
    
    insert_results = await repository.persist_docs(representations)

    rsp = api_models.BulkOperationResponse(items=insert_results)

    return rsp

@router.delete("/images/{image_uuid}/representations/{representation_uuid}")
async def delete_representation(image_uuid: str, representation_uuid: str) -> None:
    pass

@router.post("/file_references")
async def create_images(study_images: List[db_models.FileReference]) -> api_models.BulkOperationResponse:
    pass

@router.post("/collections")
async def post_collection(collection: db_models.BIACollection) -> db_models.BIACollection:
    pass

@router.post("/collections/{collection_uuid}/studies")
async def post_collection_studies(collection_uuid: str, study_uuids: List[str]) -> api_models.BulkOperationResponse:
    pass

@router.delete("/collections/{collection_uuid}/studies")
async def remove_collection_image(collection_uuid: str, study_uuids: List[str]) -> api_models.BulkOperationResponse:
    pass
