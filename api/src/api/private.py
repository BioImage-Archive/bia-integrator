import src.models.persistence as db_models
import src.models.api as api_models
import src.models.repository as repository

from typing import List, Optional
from fastapi import APIRouter, status

router = APIRouter(prefix="/api/private")

@router.post("/study", status_code=status.HTTP_201_CREATED)
async def create_study(study: db_models.BIAStudy) -> Optional[db_models.BIAStudy]:
    study_created = await repository.persist_study(study)
    return study_created

@router.patch("/study", status_code=status.HTTP_201_CREATED)
async def create_study(study: db_models.BIAStudy) -> Optional[db_models.BIAStudy]:
    study_updated = await repository.update_study(study)
    return study_updated

@router.post("/studies/{study_uuid}/refresh_counts")
async def study_refresh_counts(study_uuid: str) -> Optional[db_models.BIAStudy]:
    """Recalculate and persist counts for other objects pointing to this study."""
    repository.refresh_counts(study_uuid)

    bia_study = repository.find_study_by_id(study_uuid)
    return bia_study

@router.post("/images")
async def create_images(study_images: List[db_models.BIAImage]) -> api_models.BulkOperationResponse:
    for img in study_images:
        repository.persist_image(img)

    return None

@router.post("/images/bulk")
async def create_images() -> None:
    """TODO: Maybe file-based async?"""
    raise Exception("Not implemented")

@router.post("/images/{image_uuid}/representations")
async def post_representation(image_uuid: str, representations : List[db_models.BIAImageRepresentation]) -> api_models.BulkOperationResponse:
    pass

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
