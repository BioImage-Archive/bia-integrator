from ..models import persistence as db_models
from ..models import repository  as repository

#import models.persistence as db_models
#import models.repository as repository

from typing import List, Optional
from fastapi import APIRouter
from uuid import UUID

router = APIRouter(prefix="/api")

@router.get("/search/studies")
async def get_studies_for_collection(collection: str) -> List[str]:
    return repository.find_studies_uuid_for_collection(collection)

@router.get("/{study_uuid}")
async def get_study(study_uuid: str) -> db_models.BIAStudy:
    return await repository.find_study_by_uuid(study_uuid)

@router.get("/{study_uuid}/file_references")
async def get_study_file_references(study_uuid: str) -> db_models.FileReference:
    """@TODO: Pagination"""
    return repository.file_references_for_study(study_uuid)

@router.get("/search/images")
async def search_images(
        alias: Optional[str] = None,
        attributes: Optional[dict] = None,
        annotations: List[dict] = []
    ) -> List[db_models.BIAImage]:
    raise Exception("TODO - trickier?")
    return None

@router.get("/{study_uuid}/images")
async def get_study_images(study_uuid: str) -> db_models.BIAImage:
    """@TODO: Cursor-based pagination"""
    return repository.images_for_study(study_uuid)

# included in images now
#@router.get("/images/{image_uuid}/representations")
#async def get_image_representations(image_uuid: str, type=None) -> List[db_models.BIAImageRepresentation]:
#    pass

@router.get("/images/{image_uuid}")
async def get_image(image_uuid: str) -> db_models.BIAImage:
    return await repository.get_image(uuid=UUID(image_uuid))
    
@router.get("/images/{image_uuid}/ome_metadata")
async def get_image_ome_metadata(study_uuid: str, image_uuid: str) -> db_models.BIAOmeMetadata:
    return repository.find_image_by_id(image_uuid)

@router.get("/search/collections")
async def get_collections() -> List[db_models.BIACollection]:
    return repository.find_collections()
