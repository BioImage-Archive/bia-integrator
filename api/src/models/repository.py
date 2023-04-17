import src.models.persistence as models
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

def get_db() -> AsyncIOMotorCollection:
    mongo_connstring = "mongodb://root:example@localhost:27018/"
    client = AsyncIOMotorClient(mongo_connstring)
    return client.bia_integrator.bia_integrator

async def file_references_for_study(study_id: str):
    pass

async def images_for_study(study_id: str):
    pass

async def find_image_by_id(image_id: str):
    pass

async def refresh_counts(image_id: str):
    pass

async def persist_study(study: models.BIAStudy) -> models.BIAStudy:
    result = await get_db().insert_one(study)
    raise Exception(result)

    return study

async def find_study_by_uuid(uuid: str) -> models.BIAStudy:
    pass
