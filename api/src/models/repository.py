import src.models.persistence as models
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
from bson import ObjectId

def get_db() -> AsyncIOMotorCollection:
    mongo_connstring = "mongodb://root:example@localhost:27018/"
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

async def persist_study(study: models.BIAStudy) -> models.BIAStudy:
    result = await get_db().insert_one(study.dict())
    return await get_study(result.inserted_id)

async def update_study(study: models.BIAStudy) -> models.BIAStudy:
    result = await get_db().insert_one(study.dict())
    return await get_study(result.inserted_id)

async def find_study_by_uuid(uuid: str) -> models.BIAStudy:
    pass
