from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
)
import os
from enum import Enum
import bia_shared_datamodels.bia_data_model as shared_data_models
import pymongo
from typing import Type, List, Any
from .. import exceptions
import datetime

from bson.codec_options import CodecOptions
from bson.datetime_ms import DatetimeMS
from bson.codec_options import TypeCodec, TypeRegistry
from bson.binary import UuidRepresentation

from pydantic_core import Url

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


class UrlCodec(TypeCodec):
    python_type = Url
    bson_type = str

    def transform_python(self, value: Url) -> str:
        return str(value)

    def transform_bson(self, value: str) -> str:
        return value


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
            mongo_connstring,
            uuidRepresentation="standard",
            maxPoolSize=10,
        )
        self.db = self.connection.get_database(
            DB_NAME,
            # Looks like explicitly setting codec_options excludes settings from the client
            #   so uuid_representation needs to be defined even if already defined in connection
            codec_options=CodecOptions(
                type_registry=TypeRegistry([DateCodec(), UrlCodec()]),
                uuid_representation=UuidRepresentation.STANDARD,
            ),
        )
        self.users = self.db[COLLECTION_USERS]
        self.biaint = self.db[COLLECTION_BIA_INTEGRATOR]
        self.ome_metadata = self.db[COLLECTION_OME_METADATA]

    async def assert_model_doc_dependencies_exist(
        self, object_to_check: shared_data_models.DocumentMixin
    ):
        doc_dependencies = []
        for (
            link_attribute_name,
            link_object_reference,
        ) in object_to_check.get_object_reference_fields().items():
            if not getattr(object_to_check, link_attribute_name):
                """
                If a field is a link to another object (the for) and optional (doesn't exist as an attribute on the object to validate),
                    then if not set we skip it (because it's optional)
                    else (it's set to some non-None value) we check that the referenced object matches expected type (below)
                We don't need to check if the field itself is optional because it's typed and Pydantic does it already
                    a.i. if setting a non-optional field to None we wouldn't reach this and get an object validation error instead
                """
                continue

            link_target_options = (
                [link_object_reference.link_dest_type]
                if link_object_reference.link_dest_type
                else link_object_reference.workaround_union_reference_types
            )
            for link_target_type in link_target_options:
                if object_to_check.field_is_list(link_attribute_name):
                    for dependency_uuid in getattr(
                        object_to_check, link_attribute_name
                    ):
                        new_dependency = {
                            "uuid": dependency_uuid,
                            "model": link_target_type.get_model_metadata().model_dump(),
                        }
                        if new_dependency in doc_dependencies:
                            raise exceptions.DocumentNotFound(
                                f"Field {link_attribute_name} has duplicate dependency {dependency_uuid}"
                            )

                        doc_dependencies.append(new_dependency)
                else:
                    doc_dependencies.append(
                        {
                            "uuid": getattr(object_to_check, link_attribute_name),
                            "model": link_target_type.get_model_metadata().model_dump(),
                        }
                    )
        if not doc_dependencies:
            """
            No dependencies to check.
            No need to do a Mongo round-trip / $or with an empty list as "noop" not supported by Mongo anyway
            """
            return

        docs = await self.biaint.find(
            {"$or": doc_dependencies}, {"uuid": 1, "model": 1}
        ).to_list(length=None)
        if len(docs) != len(doc_dependencies):
            """
            ! This also fails if an object has the same object as a dependency twice.
            Feature? Could it happen for something like links in different contexts to the same file/fileref?
            """
            dependencies_missing = []

            docs_found_uuid = [doc["uuid"] for doc in docs]
            for doc_dependency in doc_dependencies:
                if doc_dependency["uuid"] not in docs_found_uuid:
                    dependencies_missing.append(doc_dependency)

            if dependencies_missing:
                raise exceptions.DocumentNotFound(
                    f"Document {object_to_check.uuid} has missing dependencies: {dependencies_missing}"
                )
            else:
                # all objects in the query (by uuid) were found in either one of the expected type options
                pass

    async def persist_doc(self, model_doc: shared_data_models.DocumentMixin):
        await self.assert_model_doc_dependencies_exist(model_doc)

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

    async def get_doc(
        self,
        uuid: shared_data_models.UUID,
        doc_type: Type[shared_data_models.DocumentMixin],
    ) -> Any:
        doc = await self._get_doc_raw(
            uuid=uuid, model=doc_type.get_model_metadata().model_dump()
        )

        if doc is None:
            raise exceptions.DocumentNotFound("Document does not exist")

        return doc_type(**doc)

    async def get_docs(
        self,
        doc_filter: dict,
        doc_type: Type[shared_data_models.DocumentMixin],
    ) -> Any:
        if not len(doc_filter.keys()):
            raise Exception("Need at least one filter")

        # @TODO: Only add additional filter for type(indexed) not version
        doc_filter["model"] = doc_type.get_model_metadata().model_dump()

        docs = []
        for doc in await self._get_docs_raw(**doc_filter):
            docs.append(doc_type(**doc))

        return docs

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

    async def _get_doc_raw(self, **kwargs) -> dict:
        doc = await self.biaint.find_one(kwargs)
        if doc:
            doc.pop("_id")

        return doc

    async def _get_docs_raw(self, **kwargs) -> List[dict]:
        docs = []

        async for doc in self.biaint.find(kwargs):
            doc.pop("_id")
            docs.append(doc)

        return docs


async def repository_create(init: bool) -> Repository:
    repository = Repository()

    if init:
        pass
        # TODO
        # await repository._init_collection_biaint()
        # await repository._init_collection_users()
        # await repository._init_collection_ome_metadata()

    return repository
