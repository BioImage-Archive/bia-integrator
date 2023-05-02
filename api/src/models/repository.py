from . import persistence as models
from ..api import exceptions

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from bson import ObjectId
from typing import List, Any

from fastapi import HTTPException


def get_db() -> AsyncIOMotorCollection:
    mongo_connstring = "mongodb://root:example@mongo1:27018/"
    client = AsyncIOMotorClient(mongo_connstring, uuidRepresentation='standard')
    return client.bia_integrator.bia_integrator

async def file_references_for_study(study_id: str):
    pass

async def images_for_study(study_id: str):
    pass

async def find_image_by_id(image_id: str):
    pass

async def refresh_counts(image_id: str):
    pass

async def get_study(id : str | ObjectId = None, **kwargs) -> models.BIAStudy:
    if id:
        kwargs['_id'] = id

    if type(kwargs.get('_id', None)) is str:
        kwargs['_id'] = ObjectId(kwargs['_id'])
    
    doc = await get_db().find_one(kwargs)
    return models.BIAStudy(**doc)

async def persist_doc(doc_model: models.DocumentMixin) -> Any:
    return await get_db().insert_one(doc_model.dict())

async def persist_docs(doc_models: List[models.DocumentMixin]) -> Any:
    rsp = await get_db().insert_many(
        doc_models.dict(),
        # if ordered=true, client stops after the first failure (e.g. duplicated uuid)
        ordered=False
    )

    # @TODO: Cleaner way to signal partial failure - return failed indices?
    return rsp

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
        raise HTTPException(404)
        raise exceptions.DocumentNotFound(f"Could not find document with uuid {doc_model.uuid} and version {doc_model.version}")
    return result

async def find_study_by_uuid(uuid: str) -> models.BIAStudy:
    return await get_study(uuid=uuid)

async def find_studies_uuid_for_collection(collection: str) -> List[str]:
    pass

async def persist_images(images: List[models.BIAImage]) -> None:
    pass