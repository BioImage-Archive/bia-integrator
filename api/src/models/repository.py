from . import persistence as models
from . import api as api_models
from ..api import exceptions

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
import pydantic
from typing import List, Any, Callable
from uuid import UUID
import pymongo
import os

DB_NAME = os.environ["DB_NAME"]
COLLECTION_BIA_INTEGRATOR = "bia_integrator"
COLLECTION_USERS = "users"

class Repository:
    connection: AsyncIOMotorClient
    db: AsyncIOMotorDatabase
    users: AsyncIOMotorCollection
    biaint: AsyncIOMotorCollection

    def __init__(self) -> None:
        mongo_connstring = os.environ["MONGO_CONNSTRING"]
        self.connection = AsyncIOMotorClient(
            mongo_connstring,
            uuidRepresentation='standard',
            maxPoolSize=10
        )
        self.db = self.connection.get_database(DB_NAME)
        self.users = self.db[COLLECTION_USERS]
        self.biaint = self.db[COLLECTION_BIA_INTEGRATOR]

    async def _init_collection_biaint(self) -> None:
        # Single collection to let mongo enforce uuid uniqueness => documents have different shape BUT
        #   indexes targeting a specific type should filter by the indexed attributes, not type
        #   so that queries don't need to be aware of the type they expect, while still hitting the index if it exists
        await self.biaint.create_index(
            [ ('uuid', 1) ],
            unique=True,
            name='doc_uuid'
        )
        self.biaint.create_index(
            [ ('accession_id', 1) ],
            unique=True,
            sparse=True,
            name='img_accession_id'
        )
        self.biaint.create_index(
            [ ('study_uuid', 1), ('alias.name', 1) ],
            unique=True,
            sparse=True,
            name='img_alias'
        )
        self.biaint.create_index(
            [ ('study_uuid', 1), ('model.type_name', 1) ],
            sparse=True,
            name='study_assets'
        )
    
    async def _init_collection_users(self) -> None:
        await self.users.create_index(
            [ ('email', 1) ],
            unique = True
        )

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
    
    def close(self):
        self.connection.close()

    async def file_references_for_study(self, *args, **kwargs) -> List[models.FileReference]:
        return await self._study_assets_find(*args, fn_model_factory=models.FileReference, **kwargs)

    async def images_for_study(self, *args, **kwargs) -> List[models.BIAImage]:
        return await self._study_assets_find(*args, fn_model_factory=models.BIAImage, **kwargs)

    async def _study_assets_find(self, study_uuid: UUID, start_uuid: UUID | None, limit: int, fn_model_factory: models.BIABaseModel) -> models.DocumentMixin:
        mongo_query = {
            'study_uuid': study_uuid,
            'model.type_name': fn_model_factory.__name__
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
        async for doc in self.biaint.find(mongo_query, limit=limit, sort=[("uuid", 1)]):
            docs.append(fn_model_factory(**doc))
        
        return docs

    async def _get_doc_raw(self, **kwargs) -> Any:        
        doc = await self.biaint.find_one(kwargs)
        return doc

    async def _get_docs_raw(self, query) -> Any:
        return await self.biaint.find(query)

    async def _doc_exists(self, doc: dict) -> bool:
        result = await self._get_doc_raw(uuid = doc['uuid'])
        if not hasattr(result, "pop"):
            return False

        result.pop('_id', None)
        # usually documents we attempt to insert/modify don't have ids, but pymongo modifies the passed dict and adds _id
        #   so if doing insert(doc), then on failure calling this, doc will actually have _id even if it didn't have it before insert
        doc.pop('_id', None)

        return result == doc

    async def _model_doc_exists(self, doc_model: models.DocumentMixin) -> bool:
        return await self._doc_exists(doc_model.dict())

    async def get_object_info(self, query: dict) -> List[api_models.ObjectInfo]:
        object_info_projection = {
            'uuid': 1,
            'model': 1
        }

        documents = []
        async for doc in self.biaint.find(query, object_info_projection):
            documents.append(api_models.ObjectInfo(**doc))
        
        return documents

    async def get_image(self, *args, **kwargs) -> models.BIAImage:
        doc = await self._get_doc_raw(*args, **kwargs)
        
        if doc is None:
            raise exceptions.DocumentNotFound('Image does not exist')
        
        return models.BIAImage(**doc)

    async def get_collection(self, *args, **kwargs) -> models.BIACollection:
        doc = await self._get_doc_raw(*args, **kwargs)
        
        if doc is None:
            raise exceptions.DocumentNotFound('Collection does not exist')
        
        return models.BIACollection(**doc)

    async def get_images(self, query) -> models.BIAImage:
        images = []
        async for doc in self.biaint.find(query):
            images.append(models.BIAImage(**doc))
        
        return images

    async def get_file_reference(self, *args, **kwargs) -> models.FileReference:
        doc = await self._get_doc_raw(*args, **kwargs)
        
        if doc is None:
            raise exceptions.DocumentNotFound('File Reference does not exist')
        
        return models.FileReference(**doc)

    async def _study_child_count(self, study_uuid: str, child_type_name: str):
        child_count = [ i async for i in
            self.biaint.aggregate([
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

    async def study_refresh_counts(self, study_uuid: str):
        # count twice instead of groupby to avoid keeping full result in memory
        file_references_count = await self._study_child_count(study_uuid, models.FileReference.__name__)
        images_count = await self._study_child_count(study_uuid, models.BIAImage.__name__)

        study = await self.find_study_by_uuid(uuid=study_uuid)
        study.file_references_count = file_references_count
        study.images_count = images_count

        study.version += 1
        await self.update_doc(study)

        return None

    async def get_study(self, *args, **kwargs) -> models.BIAStudy:
        doc = await self._get_doc_raw(*args, **kwargs)
        
        if doc is None:
            raise exceptions.DocumentNotFound('Study does not exist')
        
        return models.BIAStudy(**doc)

    async def persist_doc(self, doc_model: models.DocumentMixin) -> None:
        try:
            return await self.biaint.insert_one(doc_model.dict())
        except pymongo.errors.DuplicateKeyError as e:
            if await self._model_doc_exists(doc_model):
                return
            
            raise exceptions.InvalidUpdateException(str(e))

    async def search_studies(self, query: dict, start_uuid: UUID | None = None, limit: int = 100) -> List[models.BIAStudy]:
        studies = []

        query["model.type_name"] = "BIAStudy"
        if start_uuid:
            query["uuid"] = {
                "$gt": start_uuid
            }
        #else:
        #    query["uuid"] = {
        #        "$gt": UUID(int=0)
        #    }

        async for obj_study in self.biaint.find(query, limit=limit, sort=[("uuid", 1)]):
            studies.append(models.BIAStudy(**obj_study))
        
        return studies

    def _bulk_insert_validate_version(
            self,
            doc_models: List[models.DocumentMixin],
            ref_bulk_operation_response: api_models.BulkOperationResponse
        ) -> None:
        for idx, doc_model in enumerate(doc_models):
            if doc_model.version != 0:
                ref_bulk_operation_response.items[idx].status = 400
                ref_bulk_operation_response.items[idx].message = f"Error: Expected version to be 0, got {doc_model.version} instead"

    async def persist_docs(
            self,
            doc_models: List[models.DocumentMixin],
            ref_bulk_operation_response: api_models.BulkOperationResponse
        ) -> None:
        """
        @param insert_errors_by_uuid passed in because there might be type-specific errors

        Ideally, we should just refuse any batch inserts of the same documents, but that would call for a different response type,
            since we refuse the whole request
        """
        self._bulk_insert_validate_version(doc_models, ref_bulk_operation_response)

        insert_attempt_docs = []
        insert_attempt_docs_idx_to_doc_models_idx = []
        for idx, doc in enumerate(doc_models):
            if ref_bulk_operation_response.items[idx].status == 0: # no error yet
                insert_attempt_docs_idx_to_doc_models_idx.append(idx)
                insert_attempt_docs.append(doc.model_dump())
        
        # actual insert
        try:
            await self.biaint.insert_many(insert_attempt_docs, ordered=False)
        except pymongo.errors.BulkWriteError as e:
            for doc_write_error in e.details['writeErrors']:
                if doc_write_error['code'] == 11000 and await self._doc_exists(doc_write_error['op']):
                    # got a duplicate key error (so doc exists) but is identical to the pushed one => idempotent
                    pass
                else:
                    # either a different error, or trying to push a different version of an existing doc => error
                    insert_attempt_index = doc_write_error['index']
                    doc_model_index = insert_attempt_docs_idx_to_doc_models_idx[insert_attempt_index]
                    
                    ref_bulk_operation_response.items[doc_model_index].status = 400
                    ref_bulk_operation_response.items[doc_model_index].message = doc_write_error['errmsg']

        # remaining unchanged status codes are all for documents that were persisted
        for insert_response_item in ref_bulk_operation_response.items:
            if insert_response_item.status == 0:
                insert_response_item.status = 201

        return

    async def list_item_push(self, root_doc_uuid: str | UUID, location: str, new_list_item: pydantic.BaseModel):
        if isinstance(root_doc_uuid, str):
            root_doc_uuid = UUID(root_doc_uuid)

        result = await self.biaint.update_one(
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
            self,
            models_to_verify: List[models.DocumentMixin],
            fn_model_extract_dependency: Callable[[models.BIABaseModel], UUID],
            fn_dependency_fetch: Callable[[str | UUID], models.BIABaseModel],
            ref_bulk_operation_response: api_models.BulkOperationResponse
        ) -> None:
        # we always insert a large number of filerefs/images associated with a single dependency (study)
        # so groupby dependency before checking if it exists
        models_idx_by_dependency = {}
        for idx, model in enumerate(models_to_verify):
            model_dependency_uuid = fn_model_extract_dependency(model)
            
            if models_idx_by_dependency.get(model_dependency_uuid, None) is None:
                models_idx_by_dependency[model_dependency_uuid] = []
            
            models_idx_by_dependency[model_dependency_uuid].append(idx)

        # check dependency exists
        for dependency_uuid, models_with_dependency_idx in models_idx_by_dependency.items():
            try:
                await fn_dependency_fetch(dependency_uuid)
            except exceptions.DocumentNotFound as e:
                # if it doesn't update corresponding response item for all requested documents with the specific dependency
                for model_with_dependency_idx in models_with_dependency_idx:
                    ref_bulk_operation_response.items[model_with_dependency_idx].status = 400
                    ref_bulk_operation_response.items[model_with_dependency_idx].message = e.detail

        return

    async def update_doc(self, doc_model: models.DocumentMixin) -> None:
        result = await self.biaint.update_one(
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
            if await self._model_doc_exists(doc_model):
                return
            
            raise exceptions.DocumentNotFound(f"Could not find document with uuid {doc_model.uuid} and version {doc_model.version}")

    async def find_image_by_uuid(self, uuid: str | UUID) -> models.BIAImage:
        if isinstance(uuid, str):
            uuid = UUID(uuid)
        
        return await self.get_image(uuid=uuid)

    async def find_study_by_uuid(self, uuid: str | UUID) -> models.BIAStudy:
        if isinstance(uuid, str):
            uuid = UUID(uuid)

        return await self.get_study(uuid=uuid)

    async def search_collections(self, **kwargs) -> List[models.BIACollection]:
        mongo_query = {
            'model.type_name': 'BIACollection',
            **kwargs
        }
        
        collections = []
        async for collection in self.biaint.find(mongo_query):
            collections.append(models.BIACollection(**collection))
        
        if not len(collections):
            raise exceptions.DocumentNotFound(f"Could not find any collections matching {str(kwargs)}")
        
        return collections

async def repository_create() -> Repository:
    repository = Repository()

    collections = await repository.db.list_collection_names()
    if COLLECTION_BIA_INTEGRATOR not in collections:
        await repository._init_collection_biaint()
    if COLLECTION_USERS not in collections:
        await repository._init_collection_users()

    return repository
