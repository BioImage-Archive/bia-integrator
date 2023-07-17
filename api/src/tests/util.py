from fastapi.testclient import TestClient

from .. import app
import uuid as uuid_lib
import time

import pytest

@pytest.fixture
def api_client() -> TestClient:
    return get_client(raise_server_exceptions=False)

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
    uuid = get_uuid()

    file_reference = {
        "uuid": uuid,
        "version": 0,
        "type": "file",
        "study_uuid": existing_study['uuid'],
        "name": "test",
        "uri": "https://test.com/test",
        "size_bytes": 100
    }

    rsp = api_client.post('/api/private/file_references', json=[file_reference])
    assert rsp.status_code == 201, rsp.json()

    return file_reference


@pytest.fixture(scope="function")
def existing_image(api_client: TestClient, existing_study: dict):
    uuid = get_uuid()

    image = {
        "uuid": uuid,
        "version": 0,
        "study_uuid": existing_study['uuid'],
        "name": f"image_{uuid}",
        "original_relpath": f"/home/test/{uuid}",
        "attributes": {
            "image_uuid": uuid
        }
    }

    rsp = api_client.post('/api/private/images', json=[image])
    assert rsp.status_code == 201, rsp.json()

    return image

def get_collection(api_client: TestClient, collection_uuid: str, assert_status_code=200):
    rsp = api_client.get(f'/api/collections/{collection_uuid}')
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

    rsp = api_client.post('/api/private/collections', json=collection)
    assert rsp.status_code == 201, rsp.json()

    return get_collection(api_client, uuid)

def make_study(api_client: TestClient, study_attributes_override = {}):
    uuid = get_uuid()

    study = {
        "uuid": uuid,
        "version": 0,
        "accession_id": uuid,
        "title": "Test BIA study",
        "description": "description",
        "authors": [{
            "name": "First Author"
        }, {
            "name": "Second Author"
        }],
        "organism": "test",
        "release_date": "test"
    }
    study |= study_attributes_override

    rsp = api_client.post('/api/private/study', json=study)
    assert rsp.status_code == 201, rsp.json()

    return get_study(api_client, uuid)

def make_images(api_client: TestClient, existing_study: dict, n: int, image_template = None):
    if image_template is None:
        image_template = {
            "uuid": None,
            "version": 0,
            "study_uuid": existing_study['uuid'],
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
    images = []
    for _ in range(n):
        img = image_template.copy()
        img['uuid'] = get_uuid()
        images.append(img)
    
    rsp = api_client.post("/api/private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    return images

def make_file_references(api_client: TestClient, existing_study: dict, n: int, file_reference_template = None):
    if file_reference_template is None:
        file_reference_template = {
            "uuid": None,
            "version": 0,
            "study_uuid": existing_study['uuid'],
            "name": "test",
            "uri": "https://test.com/test",
            "size_bytes": 2,
            "attributes": {
                "k": "v"
            },
            "type": "file"
        }
    
    file_references = []
    for _ in range(n):
        file_ref = file_reference_template.copy()
        file_ref['uuid'] = get_uuid()
        file_references.append(file_ref)
    
    rsp = api_client.post("/api/private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    return file_references

def get_study(api_client: TestClient, study_uuid: str, assert_status_code=200):
    rsp = api_client.get(f'/api/studies/{study_uuid}')
    assert rsp.status_code == assert_status_code

    return rsp.json()


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

    return TestClient(app.app, **kwargs)

def get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid_lib.UUID(int=int(time.time()*1000000))

    return str(generated)
