from ..models import persistence as db_models
from ..models import api as api_models
from ..models.repository import Repository
from .exceptions import DocumentNotFound, InvalidRequestException
from . import constants
from .annotator import annotator, Annotator

from typing import List, Optional, Annotated
from fastapi import APIRouter, Query, Depends, Body
from uuid import UUID
import re

router = APIRouter(
    tags=[constants.OPENAPI_TAG_PUBLIC, constants.OPENAPI_TAG_PRIVATE]
)

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
    annotator: Annotated[Annotator, Depends(annotator)],
    db: Repository = Depends(),
    ) -> db_models.BIAStudy:
    
    study = await db.find_study_by_uuid(study_uuid)
    annotator.annotate_if_needed(study)
    
    return study

@router.get("/studies/{study_uuid}/file_references")
async def get_study_file_references(
        study_uuid: UUID,
        annotator: Annotated[Annotator, Depends(annotator)],
        start_uuid: UUID | None = None,
        limit : Annotated[int, Query(gt=0)] = 10,
        db: Repository = Depends()
    ) -> List[db_models.FileReference]:
    """
    First item in response is the next item with uuid greater than start_uuid.
    start_uuid is part of the response
    """

    study_filerefs = await db.file_references_for_study(study_uuid, start_uuid, limit)
    annotator.annotate_if_needed(study_filerefs)

    return study_filerefs

@router.get("/search/studies")
async def search_studies(
        annotator: Annotated[Annotator, Depends(annotator)],
        start_uuid: UUID | None = None,
        limit : Annotated[int, Query(gt=0)] = 10,
        db: Repository = Depends()
    ) -> List[db_models.BIAStudy]:
    """
    @TODO: Define search criteria for the general case

    First item in response is the next item with uuid greater than start_uuid.
    start_uuid is part of the response
    """
    
    studies = await db.search_studies({}, start_uuid, limit)
    annotator.annotate_if_needed(studies)

    return studies

# post because fastapi there aren't any nice ways to get fastapi to accept objects (annotations_any) in querystring
@router.post("/search/images/exact_match")
async def search_images_exact_match(
        search_filter: Annotated[api_models.SearchImageFilter, Body(embed=False)],
        annotator: Annotated[Annotator, Depends(annotator)],
        db: Repository = Depends()
    ) -> List[db_models.BIAImage]:
    """
    Exact match search of images with a specific attribute.
    Multiple parameters mean AND (as in, p1 AND p2).
    Items in lists with the `_any` suffix are ORed.

    Although `study_uuid` is optional, passing it if known is highly recommended and results in faster queries. Queries time out after 2 seconds, which should be enough for any search filtered by study.
    
    This is likely to change fast, so **named arguments are recommended** in client apps instead of positional if possible to prevent downstream breakage.
    """
    query = {}
    if search_filter.original_relpath:
        query['original_relpath'] = search_filter.original_relpath
    if search_filter.study_uuid:
        query['study_uuid'] = search_filter.study_uuid
    if search_filter.annotations_any:
        obj_annotations_any = [query_term.model_dump(exclude_defaults=True) for query_term in search_filter.annotations_any]

        query['annotations'] = {
            '$elemMatch': {
                '$or': obj_annotations_any
            }
        }
    if search_filter.image_representations_any:
        representation_filters = []
        for representation_filter in search_filter.image_representations_any:
            img_representation_list_item_filter = {}
            if representation_filter.type:
                img_representation_list_item_filter['type'] = representation_filter.type
            if representation_filter.uri_prefix:
                img_representation_list_item_filter['uri'] = {
                    '$regex': f"^{re.escape(representation_filter.uri_prefix)}",
                    '$options': 'i'
                }
            if any([representation_filter.size_bounds_gte is not None, representation_filter.size_bounds_lte is not None]):
                img_representation_list_item_filter['size'] = {}
                if representation_filter.size_bounds_gte is not None:
                    img_representation_list_item_filter['size']['$gte'] = representation_filter.size_bounds_gte
                if representation_filter.size_bounds_lte is not None:
                    img_representation_list_item_filter['size']['$lte'] = representation_filter.size_bounds_lte

            representation_filters.append(img_representation_list_item_filter)

        query['representations'] = {
            '$elemMatch': {
                '$or': representation_filters
            }
        }
    
    if query == {}:
        raise InvalidRequestException("Expecting at least one filter when searching")

    images = await db.search_images(query, start_uuid=search_filter.start_uuid, limit=search_filter.limit)
    annotator.annotate_if_needed(images)

    return images

@router.post("/search/file_references/exact_match")
async def search_file_references_exact_match(
        search_filter: Annotated[api_models.SearchFileReferenceFilter, Body(embed=False)],
        annotator: Annotated[Annotator, Depends(annotator)],
        db: Repository = Depends()
    ) -> List[db_models.FileReference]:
    """
    Exact match search of file references with a specific attribute.
    Multiple parameters mean AND (as in, p1 AND p2).
    Items in lists with the `_any` suffix are ORed.

    Although `study_uuid` is optional, passing it if known is highly recommended and results in faster queries. Queries time out after 2 seconds, which should be enough for any search filtered by study.
    
    This is likely to change fast, so **named arguments are recommended** in client apps instead of positional if possible to prevent downstream breakage.
    """
    query = {}
    if search_filter.study_uuid:
        query['study_uuid'] = search_filter.study_uuid
    if search_filter.annotations_any:
        obj_annotations_any = [query_term.model_dump(exclude_defaults=True) for query_term in search_filter.annotations_any]

        query['annotations'] = {
            '$elemMatch': {
                '$or': obj_annotations_any
            }
        }
    if search_filter.file_reference_match:
        if search_filter.file_reference_match.uri_prefix:
            query['uri'] = {
                '$regex': f"^{re.escape(search_filter.file_reference_match.uri_prefix)}",
                '$options': 'i'
            }
        if search_filter.file_reference_match.type:
            query['type'] = search_filter.file_reference_match.type
        
        if any([search_filter.file_reference_match.size_bounds_gte is not None, search_filter.file_reference_match.size_bounds_lte is not None]):
            query['size_in_bytes'] = {}
            if search_filter.file_reference_match.size_bounds_gte is not None:
                query['size_in_bytes']['$gte'] = search_filter.file_reference_match.size_bounds_gte
            if search_filter.file_reference_match.size_bounds_lte is not None:
                query['size_in_bytes']['$lte'] = search_filter.file_reference_match.size_bounds_lte

    if query == {}:
        raise InvalidRequestException("Expecting at least one filter when searching")

    file_references = await db.search_filerefs(query, start_uuid=search_filter.start_uuid, limit=search_filter.limit)
    annotator.annotate_if_needed(file_references)

    return file_references

@router.post("/search/studies/exact_match")
async def search_studies_exact_match(
        search_filter: Annotated[api_models.SearchStudyFilter, Body(embed=False)],
        annotator: Annotated[Annotator, Depends(annotator)],
        db: Repository = Depends()
    ) -> List[db_models.BIAStudy]:
    query = {}
    if search_filter.annotations_any:
        obj_annotations_any = [query_term.model_dump(exclude_defaults=True) for query_term in search_filter.annotations_any]

        query['annotations'] = {
            '$elemMatch': {
                '$or': obj_annotations_any
            }
        }
    if search_filter.study_match:
        if any([search_filter.study_match.file_references_count_gte is not None, search_filter.study_match.file_references_count_lte is not None]):
            query['file_references_count'] = {}
            if search_filter.study_match.file_references_count_gte is not None:
                query['file_references_count']['$gte'] = search_filter.study_match.file_references_count_gte
            if search_filter.study_match.file_references_count_lte is not None:
                query['file_references_count']['$lte'] = search_filter.study_match.file_references_count_lte
        if any([search_filter.study_match.images_count_gte is not None, search_filter.study_match.images_count_lte is not None]):
            query['images_count'] = {}
            if search_filter.study_match.images_count_gte is not None:
                query['images_count']['$gte'] = search_filter.study_match.images_count_gte
            if search_filter.study_match.images_count_lte is not None:
                query['images_count']['$lte'] = search_filter.study_match.images_count_lte
        if search_filter.study_match.author_name_fragment:
            query['authors'] = {
                '$elemMatch': {
                    'name': {
                        '$regex': re.escape(search_filter.study_match.author_name_fragment),
                        '$options': 'i'
                    }
                }
            }
        if search_filter.study_match.tag:
            query['tags'] = {
                '$elemMatch': {
                    '$regex': f"^{re.escape(search_filter.study_match.tag)}$",
                    '$options': 'i'
                }
            }
        if search_filter.study_match.accession_id:
            query['accession_id'] = search_filter.study_match.accession_id

    studies = await db.search_studies(query, start_uuid=search_filter.start_uuid, limit=search_filter.limit)
    annotator.annotate_if_needed(studies)

    return studies

@router.get("/studies/{study_uuid}/images")
async def get_study_images(
        study_uuid: UUID,
        annotator: Annotated[Annotator, Depends(annotator)],
        start_uuid: UUID | None = None,
        limit : Annotated[int, Query(gt=0)] = 10,
        db: Repository = Depends()
    ) -> List[db_models.BIAImage]:
    """
    First item in response is the next item with uuid greater than start_uuid.
    start_uuid is part of the response
    """

    images = await db.images_for_study(study_uuid, start_uuid, limit)
    annotator.annotate_if_needed(images)

    return images


@router.get("/images/{image_uuid}")
async def get_image(
    image_uuid: UUID,
    annotator: Annotated[Annotator, Depends(annotator)],
    db: Repository = Depends()
    ) -> db_models.BIAImage:
    
    image = await db.get_image(uuid=image_uuid)
    annotator.annotate_if_needed(image)

    return image

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
    annotator: Annotated[Annotator, Depends(annotator)],
    db: Repository = Depends()
    ) -> db_models.FileReference:
    
    file_reference = await db.get_file_reference(uuid=UUID(file_reference_uuid))
    annotator.annotate_if_needed(file_reference)

    return file_reference

#@router.get("/images/{image_uuid}/ome_metadata")
#async def get_image_ome_metadata(study_uuid: str, image_uuid: str) -> db_models.BIAOmeMetadata:
#    return repository.find_image_by_uuid(image_uuid)

@router.get("/collections")
async def search_collections(
    annotator: Annotated[Annotator, Depends(annotator)],
    name: Optional[str] = None,
    db: Repository = Depends()
) -> List[db_models.BIACollection]:

    query = {}
    if name:
        query['name'] = name

    collections = await db.search_collections(**query)
    annotator.annotate_if_needed(collections)

    return collections

@router.get("/collections/{collection_uuid}")
async def get_collection(
    collection_uuid: UUID,
    annotator: Annotated[Annotator, Depends(annotator)],
    db: Repository = Depends()
) -> db_models.BIACollection:
    
    collection = await db.get_collection(uuid=collection_uuid)
    annotator.annotate_if_needed(collection)

    return collection