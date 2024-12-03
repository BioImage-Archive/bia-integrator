from motor.motor_asyncio import (
    AsyncIOMotorClient,
    AsyncIOMotorCollection,
    AsyncIOMotorDatabase,
    AsyncIOMotorCursor,
)
import os
from enum import Enum
import bia_shared_datamodels.bia_data_model as shared_data_models
import pymongo
from typing import Type, List, Any

import pymongo.errors
from api import exceptions
from api.models.api import Pagination
from api.settings import Settings
import datetime

from bson.codec_options import CodecOptions
from bson.datetime_ms import DatetimeMS
from bson.codec_options import TypeCodec, TypeRegistry
from bson.binary import UuidRepresentation

from pydantic_core import Url
from api.api_logging import log_error


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

    def __init__(
        self,
    ) -> None:
        """
        ! Always keep params here empty
        Fastapi builds a new Repository instance for `db: Repository = Depends()`
        Which can accidetally allow api resource params to override db params
        """
        pass

    def __del__(self):
        self.connection.close()

    def configure(self, settings: Settings):
        self.connection = AsyncIOMotorClient(
            settings.mongo_connstring,
            uuidRepresentation="standard",
            maxPoolSize=settings.mongo_max_pool_size,
            timeoutms=settings.mongo_timeout_ms,
            compressors="zlib",
        )
        self.db = self.connection.get_database(
            settings.db_name,
            # Looks like explicitly setting codec_options excludes settings from the client
            #   so uuid_representation needs to be defined even if already defined in connection
            codec_options=CodecOptions(
                type_registry=TypeRegistry([DateCodec(), UrlCodec()]),
                uuid_representation=UuidRepresentation.STANDARD,
            ),
        )
        self.users = self.db[settings.mongo_collection_users]
        self.biaint = self.db[settings.mongo_collection_biaint]

    async def _add_indices_collection_biaint(self) -> None:
        await self.biaint.create_index([("uuid", 1)], unique=True, name="doc_uuid")

        await self._add_indices_reverse_links()

    async def _add_indices_collection_users(self) -> None:
        await self.users.create_index([("email", 1)], unique=True)

    async def _add_indices_reverse_links(self) -> None:
        from api.public import models_public

        existing_indexes = [
            idx["name"] for idx in await self.biaint.list_indexes().to_list()
        ]

        for model in models_public:
            model_type = model.get_model_metadata().type_name
            for (
                link_attribute_name,
                _,
            ) in model.get_object_reference_fields().items():
                name = f"{model_type.lower()}_{link_attribute_name}"

                if name not in existing_indexes:
                    try:
                        await self.biaint.create_index(
                            [(link_attribute_name, 1)],
                            partialFilterExpression={
                                "model": model.get_model_metadata().model_dump()
                            },
                            name=name,
                        )
                    except pymongo.errors.OperationFailure as e:
                        log_error("Skipping index build error", extra={"err": e})

    async def find_docs_by_link_value(
        self,
        link_attribute_in_source: str,
        link_attribute_value: str,
        source_type: Type[shared_data_models.DocumentMixin],
        pagination: Pagination,
    ):
        """
        Always use this to query for documents with a *_uuid field (documents that link to some known document)
        Ensures partialFilterExpression in _init_reverse_links_indices is added to the query so the index is used
        """

        return await self.get_docs(
            # !!!!
            # source_attribute has list values sometimes (for models that reference a list of other objects)
            #   mongo queries just so happen have the semantics we want
            # a.i. list_attribute: some_val means "any value in list_attribute is equal to some_val"
            doc_filter={link_attribute_in_source: link_attribute_value},
            doc_type=source_type,
            pagination=pagination,
        )

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

        if model_doc.version:
            """
            ! The update itself is atomic
            The error might have race conditions (but they're extremely unlikely to happen)
            """
            doc_filter = {
                "uuid": model_doc.uuid,
                "model": model_doc.model.model_dump(),
                "version": model_doc.version - 1,
            }
            result = await self.biaint.update_one(
                doc_filter,
                {"$set": model_doc.model_dump()},
                upsert=False,
            )
            if not result.matched_count:
                if not await self._get_doc_raw(uuid=model_doc.uuid):
                    raise exceptions.DocumentNotFound(
                        f"Could not find document with uuid {model_doc.uuid}"
                    )
                else:
                    # ! Keep the same InvalidUpdateException error for update and create operations (below)
                    raise exceptions.InvalidUpdateException(
                        f"Unable to update. No matches for {doc_filter}"
                    )

            return result
        else:
            try:
                return await self.biaint.insert_one(model_doc.model_dump())
            except pymongo.errors.DuplicateKeyError:
                raise exceptions.InvalidUpdateException(
                    f"Document {model_doc.uuid} already exists"
                )

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
        pagination: Pagination,
    ) -> List[Any]:
        if not len(doc_filter.keys()):
            raise Exception("Need at least one filter")

        # @TODO: Only add additional filter for type(indexed) not version
        doc_filter["model"] = doc_type.get_model_metadata().model_dump()

        docs = []
        for doc in await self._get_docs_raw(**doc_filter, pagination=pagination):
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

    def _find_paginated(
        self, collection: AsyncIOMotorCollection, query: dict, pagination: Pagination
    ) -> AsyncIOMotorCursor:
        """
        Isolates pagination implementation to keep code consistent
        """
        # @TODO: Any less awkward way to contain pagination gotchas?

        if "uuid" in query:
            # uuid filter needs to be set for pagination,
            #   we shouldn't overwrite anything that could possibly be set in the query
            # at the same time, it doesn't make sense for filters by uuid (unique) needing pagination (result set)
            #   so instead of adding something like $and: [original_filter, gt_for_pagination] just raise
            raise exceptions.GenericServerError(
                "Unsupported uuid filter for function that returns a list"
            )

        if pagination.start_from_uuid:
            query["uuid"] = {"$gt": pagination.start_from_uuid}
        else:
            # always keep a consistent order for the first page
            query["uuid"] = {"$gt": shared_data_models.UUID(int=0)}

        return collection.find(query).limit(pagination.page_size).sort("uuid")

    async def _get_docs_raw(self, pagination: Pagination, **kwargs) -> List[dict]:
        docs = []

        async for doc in self._find_paginated(self.biaint, kwargs, pagination):
            doc.pop("_id")
            docs.append(doc)

        return docs

    async def close(self):
        await self.db.close()


async def repository_create(settings: Settings) -> Repository:
    repository = Repository()
    repository.configure(settings)

    if settings.mongo_index_push:
        await repository._add_indices_collection_biaint()
        await repository._add_indices_collection_users()

    return repository
