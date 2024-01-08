from . import persistence as models
from . import api as api_models
from ..api import exceptions

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection, AsyncIOMotorDatabase
import pydantic
from typing import List, Any, Callable
import uuid
import pymongo
import os

DB_NAME = os.environ["DB_NAME"]
COLLECTION_BIA_INTEGRATOR = "bia_integrator"
COLLECTION_USERS = "users"
COLLECTION_OME_METADATA = "ome_metadata"

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
        self.ome_metadata = self.db[COLLECTION_OME_METADATA]

    async def _init_collection_biaint(self) -> None:
        # Single collection to let mongo enforce uuid uniqueness => documents have different shape BUT
        #   indexes targeting a specific type should filter by the indexed attributes, not type
        #   so that queries don't need to be aware of the type they expect, while still hitting the index if it exists
        await self.biaint.create_index(
            [ ('uuid', 1) ],
            unique=True,
            name='doc_uuid'
        )
        await self.biaint.create_index(
            [ ('accession_id', 1) ],
            unique=True,
            partialFilterExpression={
                'accession_id': {'$exists': True},
            },
            name='study_accession_id'
        )
        await self.biaint.create_index(
            [ ('study_uuid', 1), ('alias.name', 1) ],
            unique=True,
            partialFilterExpression={
                'study_uuid': {'$exists': True},
                'alias.name': {'$exists': True},
            },
            name='img_alias'
        )
        await self.biaint.create_index(
            [ ('study_uuid', 1), ('model.type_name', 1) ],
            partialFilterExpression={
                'study_uuid': {'$exists': True},
                'model.type_name': {'$exists': True},
            },
            name='study_assets'
        )
    
    async def _init_collection_users(self) -> None:
        await self.users.create_index(
            [ ('email', 1) ],
            unique = True
        )
    
    async def _init_collection_ome_metadata(self) -> None:
        await self.ome_metadata.create_index(
            [ ('bia_image_uuid', 1) ],
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

    async def _study_assets_find(self, study_uuid: uuid.UUID, start_uuid: uuid.UUID | None, limit: int, fn_model_factory: models.BIABaseModel) -> models.DocumentMixin:
        mongo_query = {
            'study_uuid': study_uuid,
            'model.type_name': fn_model_factory.__name__,
        }
        if start_uuid:
            mongo_query['uuid'] = {
                '$gt': start_uuid,
            }
        else:
            # explicitly start from the first uuid (by sorted order) if none specified
            mongo_query['uuid'] = {
                '$gt': uuid.UUID(int=0),
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
        return await self._doc_exists(doc_model.model_dump())

    async def get_object_info(self, query: dict) -> List[api_models.ObjectInfo]:
        object_info_projection = {
            'uuid': 1,
            'model': 1,
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
                            "$eq": uuid.UUID(study_uuid),
                        },
                        "model.type_name": {
                            "$eq": child_type_name,
                        },
                    },
                },
                {
                    "$count": "n_items",
                },
            ])
        ]

        return child_count[0]['n_items'] if len(child_count) else 0

    async def study_refresh_counts(self, study_uuid: str):
        # count twice instead of groupby to avoid keeping full result in memory
        file_references_count = await self._study_child_count(study_uuid, models.FileReference.__name__)
        images_count = await self._study_child_count(study_uuid, models.BIAImage.__name__)

        study = await self.find_study_by_uuid(study_uuid)
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
            return await self.biaint.insert_one(doc_model.model_dump())
        except pymongo.errors.DuplicateKeyError as e:
            if await self._model_doc_exists(doc_model):
                return
            
            raise exceptions.InvalidUpdateException(str(e))

    async def search_objects(self, query: dict, start_uuid: uuid.UUID | None = None, limit: int = 100):
        if start_uuid:
            query["uuid"] = {
                "$gt": start_uuid,
            }
        
        try:
            return await self.biaint.find(filter=query, limit=limit, sort=[("uuid", 1)], max_time_ms=2000).to_list(limit)
        except pymongo.errors.ExecutionTimeout as e:
            # Try to allow searching by most things, but set bounds on duration
            #   see */search/* before changing this
            raise exceptions.InvalidRequestException("Query timeout. Add indexed fields to reduce search set or simplify query")

    async def search_studies(self, query: dict, start_uuid: uuid.UUID | None = None, limit: int = 100) -> List[models.BIAStudy]:
        # add a study_uuid filter if it doesn't exist, so the index gets hit
        query['accession_id'] = query.get('accession_id', {"$exists": True})
        query["model.type_name"] = "BIAStudy"

        studies = []
        for study_raw in await self.search_objects(query=query, start_uuid=start_uuid, limit=limit):
            studies.append(models.BIAStudy(**study_raw))

        return studies

    async def search_images(self, query: dict, start_uuid: uuid.UUID | None = None, limit: int = 100) -> List[models.BIAImage]:
        # add a study_uuid filter if it doesn't exist, so the index gets hit
        query["study_uuid"] = query.get("study_uuid", {"$exists": True})
        query["model.type_name"] = "BIAImage"

        images = []
        for image_raw in await self.search_objects(query=query, start_uuid=start_uuid, limit=limit):
            images.append(models.BIAImage(**image_raw))
        
        return images

    async def search_filerefs(self, query: dict, start_uuid: uuid.UUID | None = None, limit: int = 100) -> List[models.FileReference]:
        # add a study_uuid filter if it doesn't exist, so the index gets hit
        query["study_uuid"] = query.get("study_uuid", {"$exists": True})
        query["model.type_name"] = "FileReference"

        filerefs = []
        for fileref_raw in await self.search_objects(query=query, start_uuid=start_uuid, limit=limit):
            filerefs.append(models.FileReference(**fileref_raw))
        
        return filerefs

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
        if len(insert_attempt_docs):
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

    async def list_item_push(self, root_doc_uuid: str | uuid.UUID, location: str, new_list_item: pydantic.BaseModel):
        if isinstance(root_doc_uuid, str):
            root_doc_uuid = uuid.UUID(root_doc_uuid)

        result = await self.biaint.update_one(
            {
                'uuid': root_doc_uuid,
            },
            {
                '$push': {
                    location: new_list_item.model_dump(),
                },
            },
            upsert=False
        )
        if not result.matched_count:
            raise exceptions.DocumentNotFound(f"Could not find document with uuid {root_doc_uuid}")
        return result

    async def doc_dependency_verify_exists(
            self,
            models_to_verify: List[models.DocumentMixin],
            fn_model_extract_dependency: Callable[[models.BIABaseModel], uuid.UUID],
            fn_dependency_fetch: Callable[[str | uuid.UUID], models.BIABaseModel],
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
                'version': doc_model.version-1,
                'model': doc_model.model.model_dump(),
            },
            {
                '$set': doc_model.model_dump(),
            },
            upsert=False
        )
        if not result.matched_count:
            if await self._model_doc_exists(doc_model):
                return
            
            raise exceptions.DocumentNotFound(f"Could not find document with uuid {doc_model.uuid} and version {doc_model.version}")

    async def find_image_by_uuid(self, image_uuid: str | uuid.UUID) -> models.BIAImage:
        if isinstance(image_uuid, str):
            image_uuid = uuid.UUID(image_uuid)
        
        return await self.get_image(uuid=image_uuid)

    async def find_study_by_uuid(self, study_uuid: str | uuid.UUID) -> models.BIAStudy:
        if isinstance(study_uuid, str):
            study_uuid = uuid.UUID(study_uuid)

        return await self.get_study(uuid=study_uuid)

    async def find_fileref_by_uuid(self, fileref_uuid: str | uuid.UUID) -> models.FileReference:
        if isinstance(fileref_uuid, str):
            fileref_uuid = uuid.UUID(fileref_uuid)
        
        return await self.get_file_reference(uuid=fileref_uuid)

    async def search_collections(self, **kwargs) -> List[models.BIACollection]:
        mongo_query = {
            'model.type_name': 'BIACollection',
            **kwargs,
        }
        
        collections = []
        async for collection in self.biaint.find(mongo_query):
            collections.append(models.BIACollection(**collection))
        
        if not len(collections):
            raise exceptions.DocumentNotFound(f"Could not find any collections matching {str(kwargs)}")
        
        return collections

    async def upsert_ome_metadata_for_image(self, image_uuid: uuid.UUID, ome_metadata: dict) -> models.BIAImageOmeMetadata:
        await self.get_image(uuid=image_uuid) # just to check it exists

        ome_metadata_model = models.BIAImageOmeMetadata(
            uuid = uuid.uuid4(),
            version = 0,
            bia_image_uuid = image_uuid,
            ome_metadata = ome_metadata
        )

        ome_metadata_dict = ome_metadata_model.model_dump()
        await self.ome_metadata.update_one(
            {'bia_image_uuid': image_uuid},
            {'$set': ome_metadata_dict},
            upsert = True
        )

        return ome_metadata_model

    async def get_ome_metadata_for_image(self, image_uuid: uuid.UUID | str) -> models.BIAImageOmeMetadata:
        if isinstance(image_uuid, str):
            image_uuid = uuid.UUID(image_uuid)

        obj_image_ome_metadata = await self.ome_metadata.find_one({'bia_image_uuid': image_uuid})
        if not obj_image_ome_metadata:
            raise exceptions.DocumentNotFound(f"No ome metadata found for image {image_uuid}")

        return models.BIAImageOmeMetadata(**obj_image_ome_metadata)

async def repository_create(init: bool) -> Repository:
    repository = Repository()

    if init:
        await repository._init_collection_biaint()
        await repository._init_collection_users()
        await repository._init_collection_ome_metadata()

    return repository
