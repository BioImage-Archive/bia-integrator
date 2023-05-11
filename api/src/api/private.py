from ..models import persistence as db_models
from ..models import repository  as repository
from ..models import api as api_models
from ..api import exceptions

from typing import List, Optional
from fastapi import APIRouter, status

router = APIRouter(prefix="/api/private")

@router.post("/study", status_code=status.HTTP_201_CREATED)
async def create_study(study: db_models.BIAStudy) -> None:
    if study.version != 0:
        raise exceptions.InvalidRequestException(f"Expecting all newly created objects to have version 0. Got {study.version}")
    
    await repository.persist_doc(study)
    
    return None

@router.patch("/study", status_code=status.HTTP_201_CREATED)
async def update_study(study: db_models.BIAStudy) -> None:
    await repository.update_doc(study)
    
    return None

@router.post("/studies/{study_uuid}/refresh_counts")
async def study_refresh_counts(study_uuid: str) -> Optional[db_models.BIAStudy]:
    """Recalculate and persist counts for other objects pointing to this study."""
    repository.refresh_counts(study_uuid)

    bia_study = repository.find_study_by_uuid(study_uuid)
    return bia_study

@router.post("/images", status_code=status.HTTP_201_CREATED)
async def create_images(study_images: List[db_models.BIAImage]) -> api_models.BulkOperationResponse:
    insert_errors_by_uuid = await repository.doc_dependency_verify_exists(study_images, lambda img: img.study_uuid, repository.find_study_by_uuid)
    insert_results = await repository.persist_docs(study_images, insert_errors_by_uuid=insert_errors_by_uuid)

    rsp = api_models.BulkOperationResponse(items=insert_results)

    return rsp

@router.patch("/images/single", status_code=status.HTTP_200_OK)
async def update_image(study_image: db_models.BIAImage) -> None:
    """Bulk update not available - update_many only has one filter for the entire update
    @TODO: Find common bulk update usecases and map them to mongo operations"""
    await repository.find_study_by_uuid(study_image.study_uuid)
    await repository.update_doc(study_image)
    
    return None

@router.post("/images/bulk")
async def create_images() -> None:
    """TODO: Maybe file-based async?"""
    raise Exception("Not implemented")

@router.post("/images/{image_uuid}/representations/single", status_code=status.HTTP_201_CREATED)
async def create_image_representation(image_uuid: str, representation : db_models.BIAImageRepresentation) -> None:
    await repository.list_item_push(image_uuid, 'representations', representation)

    return None

@router.post("/file_references", status_code=status.HTTP_201_CREATED)
async def create_file_reference(file_references: List[db_models.FileReference]) -> api_models.BulkOperationResponse:
    insert_errors_by_uuid = await repository.doc_dependency_verify_exists(file_references, lambda fr: fr.study_uuid, repository.find_study_by_uuid)
    insert_results = await repository.persist_docs(file_references, insert_errors_by_uuid=insert_errors_by_uuid)

    rsp = api_models.BulkOperationResponse(items=insert_results)
    return rsp

@router.patch("/file_references/single", status_code=status.HTTP_200_OK)
async def update_file_reference(file_reference: db_models.FileReference) -> None:
    await repository.find_study_by_uuid(file_reference.study_uuid)
    await repository.update_doc(file_reference)

    return None

@router.post("/collections", status_code=status.HTTP_201_CREATED)
async def create_collection(collection: db_models.BIACollection) -> None:
    for study_uuid in collection.study_uuids:
        await repository.find_study_by_uuid(study_uuid)
    
    await repository.persist_doc(collection)

    return None