from fastapi.testclient import TestClient

from ..api.api import app
import uuid
import time

client = TestClient(app.router, raise_server_exceptions=False)

def _get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid.UUID(int=int(time.time()))

    return str(generated)

def test_create_study():
    study = {
        "uuid": _get_uuid(),
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
    rsp = client.post('/api/private/study', json=study)
    assert rsp.status_code == 201, rsp.json()

    study_with_defaults = {
        **study,
        'imaging_type': [],
        'attributes': {},
        'annotations': [],
        'example_image_uri': "",
        'tags': [],
        'file_references_count': 0,
        'images_count': 0,
    }
    assert rsp.json() == study_with_defaults

def test_create_study_nonzero_version():
    # FIXME - map python exception to http response
    return
    study = {
        "uuid": _get_uuid(),
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
    rsp = client.post('/api/private/study', json=study)
    assert rsp.status_code == 400


def test_create_study_missing_version():
    # FIXME: RequestValidationError
    return
    """
    Leftover from same model being used internally and in the api
    In the more common case, version isn't optional"""
    study = {
        "uuid": _get_uuid(),
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
    rsp = client.post('/api/private/study', json=study)
    assert rsp.status_code == 400

def test_update_study_wrong_version():
    study = {
        "uuid": _get_uuid(),
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
    rsp = client.post('/api/private/study', json=study)
    assert rsp.status_code == 201, rsp.json()

    # re-issuing a create request shouldn't create a new object
    rsp = client.post('/api/private/study', json=study)
    assert rsp.status_code == 400

    # updating an existing object with the current version number shouldn't work
    rsp = client.patch('/api/private/study', json=study)
    assert rsp.status_code == 400

    # skipping a version when updating an object shouldn't work
    study['version'] = 2
    rsp = client.patch('/api/private/study', json=study)
    assert rsp.status_code == 400

    # updating with an incremented version number should work
    study['version'] = 1
    rsp = client.patch('/api/private/study', json=study)
    assert rsp.status_code == 200

    # updating with an old version number shouldn't work
    study['version'] = 0
    rsp = client.patch('/api/private/study', json=study)
    assert rsp.status_code == 400

    # trying to create a study was already updated shouldn't work
    study['version'] = 0
    rsp = client.post('/api/private/study', json=study)
    assert rsp.status_code == 400

def test_update_study_not_created():
    for i in range(2):
        study = {
            "uuid": _get_uuid(),
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
        rsp = client.patch('/api/private/study', json=study)
        assert rsp.status_code == 400, study

def test_update_study_nested_objects_overwritten():
    raise Exception("TODO - supposed to pull-update-push")
