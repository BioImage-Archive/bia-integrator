from ..models import persistence as db_models
from ..models.repository import Repository
from ..models import api as api_models
from ..api import exceptions
from .auth import get_current_user
from . import constants
from uuid import UUID
import logging

from typing import List
from fastapi import APIRouter, status, Depends, UploadFile, Response

from ome_types import from_xml

router = APIRouter(
    prefix="/private",
    dependencies=[Depends(get_current_user)],
    tags=[constants.OPENAPI_TAG_PRIVATE]
)

@router.post("/studies", status_code=status.HTTP_201_CREATED)
async def create_study(
    study: db_models.BIAStudy,
    db: Repository = Depends()
    ) -> None:
    
    logging.info(f"Creating study {study.accession_id}")
    if study.version != 0:
        raise exceptions.InvalidRequestException(f"Expecting all newly created objects to have version 0. Got {study.version}")
    
    await db.persist_doc(study)
    
    return None

@router.patch("/studies", status_code=status.HTTP_201_CREATED)
async def update_study(
    study: db_models.BIAStudy,
    db: Repository = Depends()
    ) -> None:
    
    logging.info(f"Updating study {study.accession_id}. New version: {study.version}")
    await db.update_doc(study)
    
    return None

@router.post("/studies/{study_uuid}/refresh_counts", status_code=status.HTTP_201_CREATED)
async def study_refresh_counts(
    study_uuid: str,
    db: Repository = Depends()
    ) -> None:
    """Recalculate and persist counts for other objects pointing to this study."""
    
    logging.info(f"Recalculating reference counts for study {study_uuid}")
    await db.study_refresh_counts(study_uuid)

    return None

@router.post("/images", status_code=status.HTTP_201_CREATED)
async def create_images(
    study_images: List[db_models.BIAImage],
    response: Response,
    db: Repository = Depends()
    ) -> api_models.BulkOperationResponse:
    
    logging.info(f"Creating {len(study_images)} images. First image attached to study: {study_images[0].study_uuid if len(study_images) else 'EMPTY LIST'}")
    # always report errors based on idx not uuid, for cases where we have multiple documents with the same uuid (they will always have different indices)
    create_bulk_response = api_models.BulkOperationResponse(
        items=[
            api_models.BulkOperationItem(
                status = 0,
                idx_in_request = idx,
                message = ""
            )
            for idx in range(len(study_images))
        ]
    )

    await db.doc_dependency_verify_exists(
        study_images,
        lambda img: img.study_uuid,
        db.find_study_by_uuid,
        ref_bulk_operation_response = create_bulk_response
    )
    await db.persist_docs(
        study_images,
        ref_bulk_operation_response = create_bulk_response
    )

    create_bulk_response.build_item_idx_by_status()
    
    if create_bulk_response.item_idx_by_status.keys() != {201}:
        response.status_code = 400

    return create_bulk_response

@router.patch("/images/single", status_code=status.HTTP_200_OK)
async def update_image(
    study_image: db_models.BIAImage,
    db: Repository = Depends()
    ) -> None:
    """Bulk update not available - update_many only has one filter for the entire update
    @TODO: Find common bulk update usecases and map them to mongo operations"""
    
    logging.info(f"Updating image {study_image.uuid}. New version: {study_image.version}")
                 
    await db.find_study_by_uuid(study_image.study_uuid)
    await db.update_doc(study_image)
    
    return None

@router.post("/images/bulk")
async def create_images_bulk() -> None:
    """TODO: Maybe file-based async?"""
    raise Exception("Not implemented")

@router.post("/images/{image_uuid}/representations/single", status_code=status.HTTP_201_CREATED)
async def create_image_representation(
    image_uuid: str,
    representation : db_models.BIAImageRepresentation,
    db: Repository = Depends()
    ) -> None:
    
    logging.info(f"Adding an image representation to image {image_uuid}")
    await db.list_item_push(image_uuid, 'representations', representation)

    return None

@router.post("/file_references", status_code=status.HTTP_201_CREATED)
async def create_file_references(
    file_references: List[db_models.FileReference],
    response: Response,
    db: Repository = Depends()
    ) -> api_models.BulkOperationResponse:
    
    logging.info(f"Creating {len(file_references)} file references. First file reference attached to study: {file_references[0].study_uuid if len(file_references) else 'EMPTY LIST'}")
    # always report errors based on idx not uuid, for cases where we have multiple documents with the same uuid (they will always have different indices)
    create_bulk_response = api_models.BulkOperationResponse(
        items=[
            api_models.BulkOperationItem(
                status = 0,
                idx_in_request = idx,
                message = ""
            )
            for idx in range(len(file_references))
        ]
    )

    await db.doc_dependency_verify_exists(
        file_references,
        lambda fr: fr.study_uuid,
        db.find_study_by_uuid,
        ref_bulk_operation_response=create_bulk_response
    )
    await db.persist_docs(file_references, ref_bulk_operation_response=create_bulk_response)

    create_bulk_response.build_item_idx_by_status()
    
    if create_bulk_response.item_idx_by_status.keys() != {201}:
        response.status_code = 400

    return create_bulk_response

@router.patch("/file_references/single", status_code=status.HTTP_200_OK)
async def update_file_reference(
    file_reference: db_models.FileReference,
    db: Repository = Depends()
    ) -> None:
    
    logging.info(f"Updating file reference {file_reference.uuid}. New version: {file_reference.version}")
    await db.find_study_by_uuid(file_reference.study_uuid)
    await db.update_doc(file_reference)

    return None

@router.post("/collections", status_code=status.HTTP_201_CREATED)
async def create_collection(
    collection: db_models.BIACollection,
    db: Repository = Depends()
    ) -> None:
    
    logging.info(f"Creating collection {collection.uuid}")
    for study_uuid in collection.study_uuids:
        await db.find_study_by_uuid(study_uuid)
    
    if collection.version == 0:
        await db.persist_doc(collection)
    else:
        await db.update_doc(collection)

    return None

@router.post("/images/{image_uuid}/ome_metadata", status_code=status.HTTP_201_CREATED)
async def set_image_ome_metadata(
    image_uuid: UUID,
    ome_metadata_file: UploadFile,
    db: Repository = Depends()
    ) -> db_models.BIAImageOmeMetadata:

    ome_metadata = from_xml(ome_metadata_file.file._file, parser='lxml', validate=True)
    bia_image_ome_metadata = await db.upsert_ome_metadata_for_image(image_uuid, ome_metadata.model_dump(mode='json'))

    return bia_image_ome_metadata