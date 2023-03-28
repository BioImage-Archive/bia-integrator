import bia_integrator_core.models as models
import bia_integrator_core.repository as repository
from typing import List, Optional

from fastapi import APIRouter, status

router = APIRouter(prefix="/studies")

@router.get("/")
async def get_studies() -> List[str]:
    """Only added for completion - add a StudyOverview model with (uuid, date_created, ...) instead"""
    return ["1","2"]

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_study(study: models.BIAStudy) -> Optional[models.BIAStudy]:
    study_created = repository.persist_study(study)
    return study_created

@router.post("/{study_id}/refresh_counts")
async def study_refresh_counts(study_id: str) -> Optional[models.BIAStudy]:
    """Recalculate and persist counts for other objects pointing to this study."""
    repository.refresh_counts(study_id)

    bia_study = repository.find_study_by_id(study_id)
    return bia_study

@router.get("/{study_id}")
async def get_study(study_id: str) -> models.BIAStudy:
    """An overview of a study
    * md list
    * md list item 2
    
    **TEST**"""
    bia_study = repository.find_study_by_id(study_id)
    return bia_study

@router.get("/{study_id}/file_references")
async def get_file_references(study_id: str) -> models.FileReference:
    """@TODO: Proper cursor-based pagination"""
    file_refs = repository.file_references_for_study(study_id)
    return file_refs

@router.get("/search/images/by-alias")
async def image_by_alias(alias: str) -> models.BIAImage:
    return None

@router.post("/images")
async def create_images(study_images: List[models.BIAImage]) -> None:
    for img in study_images:
        repository.persist_image(img)

    return None

@router.get("/{study_id}/images")
async def get_images(study_id: str) -> models.BIAImage:
    """@TODO: Proper cursor-based pagination"""
    images = repository.images_for_study(study_id)
    return images

@router.get("/{study_id}/images/{image_id}/ome_metadata")
async def get_image_ome_metadata(study_id: str, image_id: str) -> models.BIAOmeMetadata:
    """@TODO: Do we nest things by "natural domain structure" or keep them flat since we have UUIDs?"""
    images = repository.find_image_by_id(image_id)
    return images
