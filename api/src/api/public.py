from ..models import persistence as db_models
from ..models import api as api_models
from ..models.repository import Repository
from .exceptions import DocumentNotFound, InvalidRequestException
from . import constants

from typing import List, Optional, Annotated
from fastapi import APIRouter, Query, Depends, Body
from uuid import UUID
import re

router = APIRouter(tags=[constants.OPENAPI_TAG_PUBLIC, constants.OPENAPI_TAG_PRIVATE])

@router.get("/object_info_by_accessions")
async def get_object_info_by_accession(
    accessions: List[str] = Query(),
    db: Repository = Depends()
    ) -> List[api_models.ObjectInfo]:
    
    query = {
        'accession_id': {
            '$in': accessions
        }
    }
    return await db.get_object_info(query)

@router.get("/studies/{study_accession}/images_by_aliases")
async def get_study_images_by_alias(
        study_accession: str,
        aliases: List[str] = Query(),
        db: Repository = Depends()
    ) -> List[db_models.BIAImage]:
    
    study_objects_info = await db.get_object_info({
        'accession_id': study_accession
    })
    if not len(study_objects_info):
        raise DocumentNotFound(f"Study with accession {study_accession} does not exist.")

    study_object_info = study_objects_info.pop()

    query = {
        'alias.name': {
            '$in': aliases
        },
        'study_uuid': study_object_info.uuid
    }

    return await db.get_images(query)

@router.get("/studies/{study_uuid}")
async def get_study(
    study_uuid: str,
    db: Repository = Depends()
    ) -> db_models.BIAStudy:
    
    return await db.find_study_by_uuid(study_uuid)

@router.get("/studies/{study_uuid}/file_references")
async def get_study_file_references(
        study_uuid: UUID,
        start_uuid: UUID | None = None,
        limit : Annotated[int, Query(gt=0)] = 10,
        db: Repository = Depends()
    ) -> List[db_models.FileReference]:
    """
    First item in response is the next item with uuid greater than start_uuid.
    start_uuid is part of the response
    """

    return await db.file_references_for_study(study_uuid, start_uuid, limit)

@router.get("/search/studies")
async def search_studies(
        start_uuid: UUID | None = None,
        limit : Annotated[int, Query(gt=0)] = 10,
        db: Repository = Depends()
    ) -> List[db_models.BIAStudy]:
    """
    @TODO: Define search criteria for the general case

    First item in response is the next item with uuid greater than start_uuid.
    start_uuid is part of the response
    """
    
    return await db.search_studies({}, start_uuid, limit)

# post because fastapi there aren't any nice ways to get fastapi to accept objects (annotations_any) in querystring
@router.post("/search/images/exact_match")
async def search_images_exact_match(
        original_relpath: Annotated[Optional[str], Body()] = None,
        annotations_any: Annotated[List[api_models.SearchAnnotation], Body()] = [],
        image_representations_any: Annotated[List[api_models.SearchFileRepresentation], Body()] = [],
        study_uuid: Annotated[Optional[UUID], Body()] = None,
        start_uuid: Annotated[Optional[UUID], Body()] = None,
        limit : Annotated[int, Body(gt=0)] = 10,
        db: Repository = Depends()
    ) -> List[db_models.BIAImage]:
    """
    Exact match search of images with a specific attribute.
    Multiple parameters mean AND (as in, p1 AND p2).
    Items in lists with the `_any` suffix are ORed.

    Although `study_uuid` is optional, passing it if known is highly recommended and results in faster queries.
    
    This is likely to change fast, so **named arguments are recommended** in client apps instead of positional if possible to prevent downstream breakage.
    """
    query = {}
    if original_relpath:
        query['original_relpath'] = original_relpath
    if study_uuid:
        query['study_uuid'] = study_uuid
    if annotations_any:
        obj_annotations_any = [query_term.model_dump(exclude_defaults=True) for query_term in annotations_any]

        query['annotations'] = {
            '$elemMatch': {
                '$or': obj_annotations_any
            }
        }
    if image_representations_any:
        representation_filters = []
        for representation_filter in image_representations_any:
            img_representation_list_item_filter = {}
            if representation_filter.type:
                img_representation_list_item_filter['type'] = representation_filter.type
            if representation_filter.uri_prefix:
                img_representation_list_item_filter['uri'] = {
                    '$regex': f"^{re.escape(representation_filter.uri_prefix)}",
                    '$options': 'i'
                }
            if any([representation_filter.size_bounds_gte, representation_filter.size_bounds_lte]):
                img_representation_list_item_filter['size'] = {}
                if representation_filter.size_bounds_gte:
                    img_representation_list_item_filter['size']['$gte'] = representation_filter.size_bounds_gte
                if representation_filter.size_bounds_lte:
                    img_representation_list_item_filter['size']['$lte'] = representation_filter.size_bounds_lte

            representation_filters.append(img_representation_list_item_filter)

        query['representations'] = {
            '$elemMatch': {
                '$or': representation_filters
            }
        }
    
    if query == {}:
        raise InvalidRequestException("Expecting at least one filter when searching")

    return await db.search_images(query, start_uuid=start_uuid, limit=limit)

@router.get("/studies/{study_uuid}/images")
async def get_study_images(
        study_uuid: UUID,
        start_uuid: UUID | None = None,
        limit : Annotated[int, Query(gt=0)] = 10,
        db: Repository = Depends()
    ) -> List[db_models.BIAImage]:
    """
    First item in response is the next item with uuid greater than start_uuid.
    start_uuid is part of the response
    """

    return await db.images_for_study(study_uuid, start_uuid, limit)

@router.get("/images/{image_uuid}")
async def get_image(
    image_uuid: UUID,
    db: Repository = Depends()
    ) -> db_models.BIAImage:
    
    return await db.get_image(uuid=image_uuid)

@router.get("/images/{image_uuid}/ome_metadata")
async def get_image_ome_metadata(
    image_uuid: UUID,
    db: Repository = Depends()
    ) -> db_models.BIAImageOmeMetadata:
    ome_metadata = await db.get_ome_metadata_for_image(image_uuid)

    return ome_metadata
    
@router.get("/file_references/{file_reference_uuid}")
async def get_file_reference(
    file_reference_uuid: str,
    db: Repository = Depends()
    ) -> db_models.FileReference:
    
    return await db.get_file_reference(uuid=UUID(file_reference_uuid))

#@router.get("/images/{image_uuid}/ome_metadata")
#async def get_image_ome_metadata(study_uuid: str, image_uuid: str) -> db_models.BIAOmeMetadata:
#    return repository.find_image_by_uuid(image_uuid)

@router.get("/collections")
async def search_collections(
    name: Optional[str] = None,
    db: Repository = Depends()
) -> List[db_models.BIACollection]:
    
    query = {}
    if name:
        query['name'] = name

    return await db.search_collections(**query)

@router.get("/collections/{collection_uuid}")
async def get_collection(
    collection_uuid: UUID,
    db: Repository = Depends()
) -> db_models.BIACollection:
    
    return await db.get_collection(uuid=collection_uuid)
