from . import persistence as models
from . import api as api_models
from ..api import exceptions

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from bson import ObjectId
import pydantic
from typing import List, Any, Callable
from uuid import UUID
import pymongo
import json
import os

def get_db() -> AsyncIOMotorCollection:
    mongo_connstring = os.environ["DOCKER_CONNSTRING"]
    client = AsyncIOMotorClient(mongo_connstring, uuidRepresentation='standard')
    return client.bia_integrator.bia_integrator

async def file_references_for_study(*args, **kwargs) -> List[models.FileReference]:
    return await _study_assets_find(*args, fn_model_factory=models.FileReference, **kwargs)

async def images_for_study(*args, **kwargs) -> List[models.BIAImage]:
    return await _study_assets_find(*args, fn_model_factory=models.BIAImage, **kwargs)

async def _study_assets_find(study_uuid: UUID, start_uuid: UUID | None, limit: int, fn_model_factory: Any) -> models.DocumentMixin:
    mongo_query = {
        'study_uuid': study_uuid
    }
    if start_uuid:
        mongo_query['uuid'] = {
            '$gt': start_uuid
        }
    else:
        # explicitly start from the first uuid (by sorted order) if none specified
        mongo_query['uuid'] = {
            '$gt': UUID(int=0)
        }

    docs = []
    async for doc in get_db().find(mongo_query, limit=limit):
        docs.append(fn_model_factory(**doc))
    
    return docs

async def _get_doc_raw(id : str | ObjectId = None, **kwargs) -> Any:
    if id:
        kwargs['_id'] = id

    if type(kwargs.get('_id', None)) is str:
        kwargs['_id'] = ObjectId(kwargs['_id'])
    
    doc = await get_db().find_one(kwargs)
    return doc

async def get_image(*args, **kwargs) -> models.BIAImage:
    doc = await _get_doc_raw(*args, **kwargs)
    return models.BIAImage(**doc)

async def get_file_reference(*args, **kwargs) -> models.FileReference:
    doc = await _get_doc_raw(*args, **kwargs)
    return models.FileReference(**doc)

async def _study_child_count(study_uuid: str, child_type_name: str):
    child_count = [ i async for i in
        get_db().aggregate([
            {
                "$match": {
                    "study_uuid": {
                        "$eq": UUID(study_uuid)
                    },
                    "model.type_name": {
                        "$eq": child_type_name
                    }
                }
            },
            {
                "$count": "n_items"
            }
        ])
    ]

    return child_count[0]['n_items'] if len(child_count) else 0

async def study_refresh_counts(study_uuid: str):
    study = await find_study_by_uuid(uuid=study_uuid)

    # count twice instead of groupby to avoid keeping full result in memory
    study.file_references_count = await _study_child_count(study_uuid, models.FileReference.__name__)
    study.images_count = await _study_child_count(study_uuid, models.BIAImage.__name__)

    study.version += 1
    await update_doc(study)

    return None

async def get_study(*args, **kwargs) -> models.BIAStudy:
    doc = await _get_doc_raw(*args, **kwargs)
    
    if doc is None:
        raise exceptions.DocumentNotFound('Study does not exist')
    
    return models.BIAStudy(**doc)

async def persist_doc(doc_model: models.DocumentMixin) -> Any:
    try:
        return await get_db().insert_one(doc_model.dict())
    except pymongo.errors.DuplicateKeyError as e:
        raise exceptions.InvalidUpdateException(str(e))

async def persist_docs(doc_models: List[models.DocumentMixin], insert_errors_by_uuid = {}) -> List[api_models.BulkOperationItem]:
    """
    @param insert_errors_by_uuid passed in because there might be type-specific errors
    """
    doc_dicts = []

    # preliminary validation
    for doc_model in doc_models:
        if insert_errors_by_uuid.get(doc_model.uuid, None):
            # skip documents already known to have errors
            continue
        else:
            if doc_model.version == 0:
                insert_errors_by_uuid[doc_model.uuid] = {}
                doc_dicts.append(doc_model.dict())
            else:
                insert_errors_by_uuid[doc_model.uuid] = {
                    'errmsg': f'Error: Expected version to be 0, got {doc_model.version} instead'
                }

    try:
        # actual insert
        rsp = await get_db().insert_many(doc_dicts, ordered=False)
    except pymongo.errors.BulkWriteError as e:
        doc_write_errors = [
            {
                'index': doc_write_error['index'],
                'errmsg': doc_write_error['errmsg'],
                'uuid': doc_write_error['op']['uuid']
            }
            for doc_write_error in e.details['writeErrors']
        ]
        documents_with_insert_info = len(doc_write_errors) + e.details['nInserted']
        if documents_with_insert_info != len(doc_dicts):
            # this should never happen, but maybe something behaves unexpectedly under load?
            raise Exception(f"""Tried to bulk insert {len(doc_dicts)} documents, received information on only {documents_with_insert_info}
                            Successfully inserted: {e.details['nInserted']}
                            Documents with errors, but accounted for: {json.dumps(doc_write_errors)}
                            """)

        for write_error in doc_write_errors:
            insert_errors_by_uuid[write_error['uuid']] = write_error
    else:
        pass

    # map errors to insert items
    insert_results = []
    for idx, doc_model in enumerate(doc_models):
        if insert_errors_by_uuid[doc_model.uuid] == {}:
            insert_results.append(api_models.BulkOperationItem(
                status=201,
                idx_in_request=idx,
                message=''
            ))
        else:
            insert_results.append(api_models.BulkOperationItem(
                status=400,
                idx_in_request=idx,
                message=insert_errors_by_uuid[doc_model.uuid]['errmsg']
            ))

    return insert_results

async def list_item_push(root_doc_uuid: str | UUID, location: str, new_list_item: pydantic.BaseModel):
    if isinstance(root_doc_uuid, str):
        root_doc_uuid = UUID(root_doc_uuid)

    result = await get_db().update_one(
        {
            'uuid': root_doc_uuid
        },    
        {
            '$push': {
                location: new_list_item.dict()
            }
        },
        upsert=False
    )
    if not result.matched_count:
        raise exceptions.DocumentNotFound(f"Could not find document with uuid {root_doc_uuid}")
    return result

async def doc_dependency_verify_exists(
        models_to_verify: List[models.DocumentMixin],
        fn_model_extract_dependency: Callable[[models.BIABaseModel], UUID],
        fn_dependency_fetch: Callable[[str | UUID], models.BIABaseModel]
    ) -> dict:
    """
    @return 
    """
    dependency_errors_by_model_uuid = {}

    dependency_errors_by_dependency_uuid = {
        fn_model_extract_dependency(model): None
        for model in models_to_verify
    }

    for dependency_uuid in dependency_errors_by_dependency_uuid.keys():
        try:
            await fn_dependency_fetch(dependency_uuid)
        except exceptions.DocumentNotFound as e:
            dependency_errors_by_dependency_uuid[dependency_uuid] = e
    if any([v for v in dependency_errors_by_dependency_uuid if v is not None]):
        for model in models_to_verify:
            dependency_uuid = fn_model_extract_dependency(model)
            dependency_error = dependency_errors_by_dependency_uuid[dependency_uuid]
            if dependency_error:
                dependency_errors_by_model_uuid[model.uuid] = {
                    'errmsg': dependency_error.detail
                }

    return dependency_errors_by_model_uuid


async def update_doc(doc_model: models.DocumentMixin) -> Any:
    result = await get_db().update_one(
        {
            'uuid': doc_model.uuid,
            'version': doc_model.version-1
        },    
        {
            '$set': doc_model.dict()
        },
        upsert=False
    )
    if not result.matched_count:
        raise exceptions.DocumentNotFound(f"Could not find document with uuid {doc_model.uuid} and version {doc_model.version}")
    return result

async def find_image_by_uuid(uuid: str | UUID) -> models.BIAImage:
    if isinstance(uuid, str):
        uuid = UUID(uuid)
    
    return await get_image(uuid=uuid)

async def find_study_by_uuid(uuid: str | UUID) -> models.BIAStudy:
    if isinstance(uuid, str):
        uuid = UUID(uuid)

    return await get_study(uuid=uuid)

async def find_studies_uuid_for_collection(collection: str) -> List[str]:
    pass

async def persist_images(images: List[models.BIAImage]) -> None:
    pass