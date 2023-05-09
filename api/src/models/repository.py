from . import persistence as models
from . import api as api_models
from ..api import exceptions

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from bson import ObjectId
from typing import List, Any
from uuid import UUID
import pymongo
import json

def get_db() -> AsyncIOMotorCollection:
    mongo_connstring = "mongodb://root:example@mongo1:27018/"
    client = AsyncIOMotorClient(mongo_connstring, uuidRepresentation='standard')
    return client.bia_integrator.bia_integrator

async def file_references_for_study(study_id: str):
    pass

async def images_for_study(study_id: str):
    pass

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

async def refresh_counts(image_id: str):
    pass

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