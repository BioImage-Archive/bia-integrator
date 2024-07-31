from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
import os
from enum import Enum
import bia_shared_datamodels.bia_data_model as shared_data_models
import pymongo
from typing import Any
from .. import exceptions
import datetime

from bson.codec_options import CodecOptions
from bson.datetime_ms import DatetimeMS
from bson.codec_options import TypeCodec, TypeRegistry
from bson.binary import UuidRepresentation


DB_NAME = os.environ["DB_NAME"]
COLLECTION_BIA_INTEGRATOR = "bia_integrator"
COLLECTION_USERS = "users"
COLLECTION_OME_METADATA = "ome_metadata"


class DateCodec(TypeCodec):
    python_type = datetime.date  # the Python type acted upon by this type codec
    bson_type = DatetimeMS  # the BSON type acted upon by this type codec

    def transform_python(self, value: datetime.date) -> DatetimeMS:
        same_day_zero_time = datetime.datetime.combine(
            value, datetime.datetime.min.time()
        )

        return DatetimeMS(value=same_day_zero_time)

    def transform_bson(self, value: DatetimeMS) -> datetime.date:
        return value.as_datetime().date()


class OverwriteMode(str, Enum):
    FAIL = "fail"
    ALLOW_IDEMPOTENT = "allow_idempotent"


class Repository:
    connection: AsyncIOMotorClient
    db: AsyncIOMotorDatabase
    users: AsyncIOMotorCollection
    biaint: AsyncIOMotorCollection
    overwrite_mode: OverwriteMode = OverwriteMode.FAIL

    def __init__(self) -> None:
        mongo_connstring = os.environ["MONGO_CONNSTRING"]
        self.connection = AsyncIOMotorClient(
            mongo_connstring, uuidRepresentation="standard", maxPoolSize=10
        )
        self.db = self.connection.get_database(
            DB_NAME,
            # Looks like explicitly setting codec_options excludes settings from the client
            #   so uuid_representation needs to be defined even if already defined in connection
            codec_options=CodecOptions(
                type_registry=TypeRegistry([DateCodec()]),
                uuid_representation=UuidRepresentation.STANDARD,
            ),
        )
        self.users = self.db[COLLECTION_USERS]
        self.biaint = self.db[COLLECTION_BIA_INTEGRATOR]
        self.ome_metadata = self.db[COLLECTION_OME_METADATA]

    async def persist_doc(self, model_doc: shared_data_models.DocumentMixin):
        try:
            return await self.biaint.insert_one(model_doc.model_dump())
        except pymongo.errors.DuplicateKeyError as e:
            if (
                (e.details["code"] == 11000)
                and (self.overwrite_mode == OverwriteMode.ALLOW_IDEMPOTENT)
                and (await self._model_doc_exists(model_doc))
            ):
                return

            raise exceptions.InvalidUpdateException(str(e))

    async def get_doc(self, uuid: shared_data_models.UUID, doc_type):
        doc = await self._get_doc_raw(uuid=uuid)

        if doc is None:
            raise exceptions.DocumentNotFound("Study does not exist")

        return doc_type(**doc)

    async def _model_doc_exists(
        self, doc_model: shared_data_models.DocumentMixin
    ) -> bool:
        return await self._doc_exists(doc_model.model_dump())

    async def _doc_exists(self, doc: dict) -> bool:
        result = await self._get_doc_raw(uuid=doc["uuid"])
        if not hasattr(result, "pop"):
            return False

        result.pop("_id", None)
        # usually documents we attempt to insert/modify don't have ids, but pymongo modifies the passed dict and adds _id
        #   so if doing insert(doc), then on failure calling this, doc will actually have _id even if it didn't have it before insert
        doc.pop("_id", None)

        return result == doc

    async def _get_doc_raw(self, **kwargs) -> Any:
        doc = await self.biaint.find_one(kwargs)
        doc.pop("_id")

        return doc


async def repository_create(init: bool) -> Repository:
    repository = Repository()

    if init:
        pass
        # TODO
        # await repository._init_collection_biaint()
        # await repository._init_collection_users()
        # await repository._init_collection_ome_metadata()

    return repository
