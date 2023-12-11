from fastapi.testclient import TestClient

from .. import app
import uuid as uuid_lib
from typing import List
import time

import pytest
import pytest_asyncio
from ..models.repository import repository_create, Repository
from ..api.auth import create_user, get_user
import asyncio

#@pytest.fixture
#def api_client_private() -> TestClient:
#    client = get_client(raise_server_exceptions=False)
#    authenticate_client(client)

#    return client

@pytest.fixture
def api_client() -> TestClient:
    client = get_client(raise_server_exceptions=False)
    authenticate_client(client) #@TODO: DELETEME

    return client

@pytest.fixture(scope="function")
def uuid() -> str:
    return get_uuid()

@pytest.fixture(scope="function")
def existing_study(api_client: TestClient):
    return make_study(api_client)

@pytest.fixture(scope="function")
def existing_collection(api_client: TestClient):
    return make_collection(api_client)

@pytest.fixture(scope="function")
def existing_file_reference(api_client: TestClient, existing_study: dict):
    file_reference = get_template_file_reference(existing_study, add_uuid=True)

    rsp = api_client.post('private/file_references', json=[file_reference])
    assert rsp.status_code == 201, rsp.json()

    rsp_get_fileref = api_client.get(f"file_references/{file_reference['uuid']}")
    assert rsp_get_fileref.status_code == 200

    return rsp_get_fileref.json()

@pytest.fixture(scope="function")
def existing_image(api_client: TestClient, existing_study: dict):
    image = get_template_image(existing_study, add_uuid=True)

    rsp = api_client.post('private/images', json=[image])
    assert rsp.status_code == 201, rsp.json()

    rsp_get_image = api_client.get(f"images/{image['uuid']}")
    assert rsp_get_image.status_code == 200

    return rsp_get_image.json()

class DBTestMixin:
    @pytest_asyncio.fixture
    async def db(self) -> Repository:
        return await repository_create(init = True)

def create_user_if_missing(email: str, password: str):
    """
    Exception from the general rule used in this project, of tests being as high-level as possible
    Just to avoid compromising on security for easy test user creation / the logistics of a seed db 
    """
    loop = asyncio.get_event_loop()

    async def create_test_user_if_missing():
        db = await repository_create(init = True)

        if not await get_user(db, email):
            await create_user(db, email, password)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_test_user_if_missing())

def authenticate_client(api_client: TestClient):
    user_details = {
        "username": "test@example.com",
        "password": "test"
    }
    create_user_if_missing(user_details['username'], user_details['password'])

    rsp = api_client.post("auth/token", data=user_details)

    assert rsp.status_code == 200
    token = rsp.json()

    api_client.headers["Authorization"] = f"Bearer {token['access_token']}"

def get_collection(api_client: TestClient, collection_uuid: str, assert_status_code=200):
    rsp = api_client.get(f'collections/{collection_uuid}')
    assert rsp.status_code == assert_status_code

    return rsp.json()

def make_collection(api_client: TestClient, collection_attributes_override = {}):
    uuid = get_uuid()
    collection = {
        "uuid": uuid,
        "version": 0,
        "name": "test_collection_name",
        "title": "test_collection_title",
        "subtitle": "test_collection_subtitle",
        "description": "test_collection_description",
        "study_uuids": []
    }
    collection |= collection_attributes_override

    rsp = api_client.post('private/collections', json=collection)
    assert rsp.status_code == 201, rsp.json()

    return get_collection(api_client, uuid)

def get_template_study(add_uuid = False):
    study_uuid = None if not add_uuid else get_uuid()
    return {
        "uuid": study_uuid,
        "version": 0,
        "model": {"type_name": "BIAStudy", "version": 1},
        "accession_id": study_uuid,
        "title": "Test BIA study",
        "description": "description",
        "attributes": {},
        "annotations": [],
        "example_image_annotation_uri": '',
        "example_image_uri": '',
        "imaging_type": None,
        "authors": [],
        "tags": [],
        "organism": "test",
        "release_date": "test",
        "file_references_count": 0,
        "images_count": 0,
        "annotations_applied": False
    }

def make_study(api_client: TestClient, study_attributes_override = {}):
    study = get_template_study(add_uuid=True)
    study |= study_attributes_override

    """
    {
        "name": "First Author"
    }, {
        "name": "Second Author"
    }
    """

    rsp = api_client.post('private/studies', json=study)
    assert rsp.status_code == 201, rsp.json()

    return get_study(api_client, study['uuid'])

def get_template_file_reference(existing_study: dict, add_uuid = False):
    return {
        "uuid": None if not add_uuid else get_uuid(),
        "version": 0,
        "study_uuid": existing_study['uuid'],
        'model': {'type_name': 'FileReference', 'version': 1},
        "name": "test",
        "uri": "https://test.com/test",
        "size_in_bytes": 2,
        "attributes": {},
        "annotations": [],
        "type": "file"
    }

def get_template_collection(add_uuid = False):
    return {
        "uuid": None if not add_uuid else get_uuid(),
        "version": 0,
        "model": {"type_name": "BIACollection", "version": 1},
        "name": "template_collection_name",
        "title": "template_collection_title",
        "subtitle": "template_collection_subtitle",
        "description": "template_collection_description",
        "study_uuids": [],
        "attributes": {},
        "annotations": []
    }

def get_template_image(existing_study: dict, add_uuid = False):
    return {
        "uuid": None if not add_uuid else get_uuid(),
        "version": 0,
        "study_uuid": existing_study['uuid'],
        'model': {'type_name': 'BIAImage', 'version': 1},
        "name": f"image_name_value",
        "original_relpath": f"/home/test/image_path_value",
        "attributes": {
            "k": "v"
        },
        "annotations": [],
        "dimensions": None,
        "alias": None,  
        "representations": []
    }

def make_images(api_client: TestClient, existing_study: dict, n: int, image_template = None, expect_status = 201):
    if image_template is None:
        image_template = get_template_image(existing_study)

    images = []
    for _ in range(n):
        img = image_template.copy()
        if not img['uuid']:
            img['uuid'] = get_uuid()

        images.append(img)
    
    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == expect_status, rsp.json()

    return images

def make_file_references(api_client: TestClient, existing_study: dict, n: int, file_reference_template = None):
    if file_reference_template is None:
        file_reference_template = get_template_file_reference(existing_study)
    
    file_references = []
    for _ in range(n):
        file_ref = file_reference_template.copy()
        if not file_ref['uuid']:
            file_ref['uuid'] = get_uuid()

        file_references.append(file_ref)
    
    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    return file_references

def get_study(api_client: TestClient, study_uuid: str, assert_status_code=200):
    rsp = api_client.get(f'studies/{study_uuid}')
    assert rsp.status_code == assert_status_code

    return rsp.json()

TEST_SERVER_BASE_URL = "http://localhost.com/api/v1"
def get_client(**kwargs) -> TestClient:
    from fastapi.responses import JSONResponse
    from fastapi import Request
    import traceback

    @app.app.exception_handler(Exception)
    def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=traceback.format_exception(exc, value=exc, tb=exc.__traceback__),
        )

    return TestClient(app.app, base_url=TEST_SERVER_BASE_URL, **kwargs)

def get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid_lib.UUID(int=int(time.time()*1000000))

    return str(generated)

def assert_bulk_response_items_correct(
        api_client: TestClient,
        bulk_create_payload: List[dict],
        bulk_create_response: dict,
        single_item_get_path: str
    ):
    for response_item in bulk_create_response['items']:
        created_item = bulk_create_payload[response_item['idx_in_request']]
        rsp = api_client.get(f"{single_item_get_path}/{created_item['uuid']}")
        
        if response_item['status'] == 201:
            assert rsp.status_code == 200
            fetched_item = rsp.json()
            assert fetched_item == created_item
        elif response_item['status'] == 400:
            if response_item['message'].startswith("E11000 duplicate key error collection"):
                # clashing with existing document
                # check that the other document exists and is different from the attempted insert 
                assert rsp.status_code == 200

                # only check the attributes in the request item, to avoid the check always passing due to model changes
                existing_item = rsp.json()
                existing_item_shaped_as_request = {
                    k: existing_item[k]
                    for k in created_item.keys()
                }
                assert existing_item_shaped_as_request != created_item
            else:
                # if there was no clash but the insert was rejected, the object shouldn't exist at all
                assert rsp.status_code == 404
