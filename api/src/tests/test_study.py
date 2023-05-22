from fastapi.testclient import TestClient
from .util import *

def test_create_study(api_client: TestClient, uuid: str):
    study = {
        "uuid": uuid,
        "version": 0,
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
    rsp = api_client.post('/api/private/study', json=study)
    assert rsp.status_code == 201, str(rsp)

    study_with_defaults = {
        **study,
        'imaging_type': [],
        'attributes': {},
        'annotations': [],
        'example_image_uri': "",
        'tags': [],
        'file_references_count': 0,
        'images_count': 0,
        'model': {'type_name': 'BIAStudy', 'version': 1}
    }

    study_created = get_study(api_client, uuid)
    assert type(study_created['_id']) == str
    del study_created['_id']

    assert study_created == study_with_defaults

def test_create_study_nonzero_version(api_client: TestClient, uuid: str):
    study = {
        "uuid": uuid,
        "version": 1,
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
    rsp = api_client.post('/api/private/study', json=study)
    assert rsp.status_code == 422


def test_create_study_missing_version(api_client: TestClient, uuid: str):
    """
    Leftover from same model being used internally and in the api
    In the more common case, version isn't optional"""
    study = {
        "uuid": uuid,
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
    rsp = api_client.post('/api/private/study', json=study)
    assert rsp.status_code == 422

def test_update_study_wrong_version(api_client: TestClient, uuid: str):
    study = {
        "uuid": uuid,
        "version": 0,
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
    rsp = api_client.post('/api/private/study', json=study)
    assert rsp.status_code == 201, rsp.json()

    # re-issuing a create request shouldn't create a new object
    rsp = api_client.post('/api/private/study', json=study)
    assert rsp.status_code == 409

    # updating an existing object with the current version number shouldn't work
    rsp = api_client.patch('/api/private/study', json=study)
    assert rsp.status_code == 404

    # skipping a version when updating an object shouldn't work
    study['version'] = 2
    rsp = api_client.patch('/api/private/study', json=study)
    assert rsp.status_code == 404

    # updating with an incremented version number should work
    study['version'] = 1
    rsp = api_client.patch('/api/private/study', json=study)
    assert rsp.status_code == 201

    # updating with an old version number shouldn't work
    study['version'] = 0
    rsp = api_client.patch('/api/private/study', json=study)
    assert rsp.status_code == 404

    # trying to create a study was already updated shouldn't work
    study['version'] = 0
    rsp = api_client.post('/api/private/study', json=study)
    assert rsp.status_code == 409

def test_update_study_not_created(api_client: TestClient, uuid: str):
    for i in range(2):
        study = {
            "uuid": uuid,
            "version": i,
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
        rsp = api_client.patch('/api/private/study', json=study)
        assert rsp.status_code == 404, str(rsp)

def test_update_study_nested_objects_overwritten(api_client: TestClient, existing_study: dict):
    new_title = "Updated title"
    new_authors_list = [{
        "name": "New author1"
    },{
        "name": "New author2"
    }]

    existing_study["title"] = new_title
    existing_study["authors"] = new_authors_list
    existing_study["version"] = 1

    rsp = api_client.patch('/api/private/study', json=existing_study)
    assert rsp.status_code == 201

    study = api_client.get(f'/api/{existing_study["uuid"]}').json()
    assert study["authors"] == new_authors_list
    assert study["title"] == new_title
    assert study["version"] == 1
    assert study["uuid"] == existing_study["uuid"]

    # check changed that shouldn't
    for attr in ["authors", "title", "version"]:
        del study[attr]
        del existing_study[attr]
    assert study == existing_study
