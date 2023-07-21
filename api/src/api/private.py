from ..models import persistence as db_models
from ..models import repository  as repository
from ..models import api as api_models
from ..api import exceptions
import logging

from typing import List, Optional
from fastapi import APIRouter, status

router = APIRouter(prefix="/api/private")

@router.post("/study", status_code=status.HTTP_201_CREATED)
async def create_study(study: db_models.BIAStudy) -> None:
    logging.info(f"Creating study {study.accession_id}")

    if study.version != 0:
        raise exceptions.InvalidRequestException(f"Expecting all newly created objects to have version 0. Got {study.version}")
    
    await repository.persist_doc(study)
    
    return None

@router.patch("/study", status_code=status.HTTP_201_CREATED)
async def update_study(study: db_models.BIAStudy) -> None:
    logging.info(f"Updating study {study.accession_id}. New version: {study.version}")

    await repository.update_doc(study)
    
    return None

@router.post("/studies/{study_uuid}/refresh_counts", status_code=status.HTTP_201_CREATED)
async def study_refresh_counts(study_uuid: str) -> None:
    """Recalculate and persist counts for other objects pointing to this study."""
    logging.info(f"Recalculating reference counts for study {study_uuid}")

    await repository.study_refresh_counts(study_uuid)

    return None

@router.post("/images", status_code=status.HTTP_201_CREATED)
async def create_images(study_images: List[db_models.BIAImage]) -> api_models.BulkOperationResponse:
    logging.info(f"Creating {len(study_images)} images. First image attached to study: {study_images[0].study_uuid if len(study_images) else 'EMPTY LIST'}")

    insert_errors_by_uuid = await repository.doc_dependency_verify_exists(study_images, lambda img: img.study_uuid, repository.find_study_by_uuid)
    insert_results = await repository.persist_docs(study_images, insert_errors_by_uuid=insert_errors_by_uuid)

    rsp = api_models.BulkOperationResponse(items=insert_results)

    return rsp

@router.patch("/images/single", status_code=status.HTTP_200_OK)
async def update_image(study_image: db_models.BIAImage) -> None:
    """Bulk update not available - update_many only has one filter for the entire update
    @TODO: Find common bulk update usecases and map them to mongo operations"""
    logging.info(f"Updating image {study_image.uuid}. New version: {study_image.version}")
                 
    await repository.find_study_by_uuid(study_image.study_uuid)
    await repository.update_doc(study_image)
    
    return None

@router.post("/images/bulk")
async def create_images() -> None:
    """TODO: Maybe file-based async?"""
    raise Exception("Not implemented")

@router.post("/images/{image_uuid}/representations/single", status_code=status.HTTP_201_CREATED)
async def create_image_representation(image_uuid: str, representation : db_models.BIAImageRepresentation) -> None:
    logging.info(f"Adding an image representation to image {image_uuid}")

    await repository.list_item_push(image_uuid, 'representations', representation)

    return None

@router.post("/file_references", status_code=status.HTTP_201_CREATED)
async def create_file_reference(file_references: List[db_models.FileReference]) -> api_models.BulkOperationResponse:
    logging.info(f"Creating {len(file_references)} file references. First file reference attached to study: {file_references[0].study_uuid if len(file_references) else 'EMPTY LIST'}")

    insert_errors_by_uuid = await repository.doc_dependency_verify_exists(file_references, lambda fr: fr.study_uuid, repository.find_study_by_uuid)
    insert_results = await repository.persist_docs(file_references, insert_errors_by_uuid=insert_errors_by_uuid)

    rsp = api_models.BulkOperationResponse(items=insert_results)
    return rsp

@router.patch("/file_references/single", status_code=status.HTTP_200_OK)
async def update_file_reference(file_reference: db_models.FileReference) -> None:
    logging.info(f"Updating file reference {file_reference.uuid}. New version: {file_reference.version}")

    await repository.find_study_by_uuid(file_reference.study_uuid)
    await repository.update_doc(file_reference)

    return None

@router.post("/collections", status_code=status.HTTP_201_CREATED)
async def create_collection(collection: db_models.BIACollection) -> None:
    logging.info(f"Creating collection {collection.uuid}")

    for study_uuid in collection.study_uuids:
        await repository.find_study_by_uuid(study_uuid)
    
    if collection.version == 0:
        await repository.persist_doc(collection)
    else:
        await repository.update_doc(collection)

    return None
