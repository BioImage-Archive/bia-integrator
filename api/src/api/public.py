from ..models import persistence as db_models
from ..models import api as api_models
from ..models import repository  as repository

from typing import List, Optional, Annotated
from fastapi import APIRouter, Query
from uuid import UUID

router = APIRouter(prefix="/api")

@router.get("/object_info_by_accessions")
async def get_object_info_by_accession(accessions: List[str] = Query()) -> List[api_models.ObjectInfo]:
    query = {
        'accession_id': {
            '$in': accessions
        }
    }
    return await repository.get_object_info(query)

@router.get("/object_info_by_aliases")
async def get_object_info_by_alias(aliases: List[str] = Query()) -> List[api_models.ObjectInfo]:
    query = {
        'image_aliases.name': {
            '$in': aliases
        }
    }

    return await repository.get_object_info(query)

@router.get("/{study_uuid}")
async def get_study(study_uuid: str) -> db_models.BIAStudy:
    return await repository.find_study_by_uuid(study_uuid)

@router.get("/{study_uuid}/file_references")
async def get_study_file_references(
        study_uuid: UUID,
        start_uuid: UUID | None = None,
        limit : Annotated[int, Query(gt=0)] = 10
    ) -> List[db_models.FileReference]:
    return await repository.file_references_for_study(study_uuid, start_uuid, limit)

@router.get("/search/images")
async def search_images(
        alias: Optional[str] = None,
        attributes: Optional[dict] = None,
        annotations: List[dict] = []
    ) -> List[db_models.BIAImage]:
    raise Exception("TODO - trickier?")
    return None

@router.get("/{study_uuid}/images")
async def get_study_images(study_uuid: UUID, start_uuid: UUID | None = None, limit : Annotated[int, Query(gt=0)] = 10) -> List[db_models.BIAImage]:    
    return await repository.images_for_study(study_uuid, start_uuid, limit)

@router.get("/images/{image_uuid}")
async def get_image(image_uuid: UUID) -> db_models.BIAImage:
    return await repository.get_image(uuid=image_uuid)
    
@router.get("/file_references/{file_reference_uuid}")
async def get_image(file_reference_uuid: str) -> db_models.FileReference:
    return await repository.get_file_reference(uuid=UUID(file_reference_uuid))

@router.get("/images/{image_uuid}/ome_metadata")
async def get_image_ome_metadata(study_uuid: str, image_uuid: str) -> db_models.BIAOmeMetadata:
    return repository.find_image_by_uuid(image_uuid)

@router.get("/collections")
async def search_collections(
    name: Optional[str] = None
) -> List[db_models.BIACollection]:
    return await repository.search_collections(name=name)

