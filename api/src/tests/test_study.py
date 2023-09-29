from fastapi.testclient import TestClient
from .util import *

def test_create_study(api_client: TestClient, uuid: str):
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
    rsp = api_client.post('/api/private/studies', json=study)
    assert rsp.status_code == 201, str(rsp)

    study_with_defaults = {
        **study,
        'imaging_type': None,
        'attributes': {},
        'annotations': [],
        'example_image_uri': "",
        'example_image_annotation_uri': "",
        'tags': [],
        'file_references_count': 0,
        'images_count': 0,
        'model': {'type_name': 'BIAStudy', 'version': 1}
    }

    study_created = get_study(api_client, uuid)

    assert study_created == study_with_defaults

def test_study_annotations_applied(api_client: TestClient, uuid: str):
    study = {
        "uuid": uuid,
        "version": 0,
        'accession_id': uuid,
        "title": "Test BIA study",
        "description": "description",
        "authors": [{
            "name": "First Author"
        }, {
            "name": "Second Author"
        }],
        "organism": "test",
        "release_date": "test",
        "annotations": [{
            "author_email": "test@ebi.ac.uk",
            "key": "organism",
            "value": "should_overwrite_existing_organism",
            "state": "active"
        },{
            "author_email": "test@ebi.ac.uk",
            "key": "custom_annotation",
            "value": "should_only_be_added_as_an_attribute",
            "state": "active"
        },{
            "author_email": "test@ebi.ac.uk",
            "key": "example_image_uri",
            "value": "should_overwrite_model-default_attributes_added_after_deserialization",
            "state": "active"
        }]
    }
    rsp = api_client.post('/api/private/studies', json=study)
    assert rsp.status_code == 201, str(rsp)

    study_created = get_study(api_client, uuid)

    assert study_created['organism'] == 'should_overwrite_existing_organism'
    assert 'custom_annotation' not in study_created.keys()
    assert study_created['attributes']['custom_annotation'] == 'should_only_be_added_as_an_attribute'
    assert study_created['example_image_uri'] == 'should_overwrite_model-default_attributes_added_after_deserialization'


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
    rsp = api_client.post('/api/private/studies', json=study)
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
    rsp = api_client.post('/api/private/studies', json=study)
    assert rsp.status_code == 422

def test_update_study_wrong_version(api_client: TestClient, uuid: str):
    study = {
        "uuid": uuid,
        "version": 0,
        'accession_id': uuid,
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
    rsp = api_client.post('/api/private/studies', json=study)
    assert rsp.status_code == 201, rsp.json()

    # re-issuing a create request shouldn't create a new object
    rsp = api_client.post('/api/private/studies', json=study)
    assert rsp.status_code == 409

    # updating an existing object with the current version number shouldn't work
    rsp = api_client.patch('/api/private/studies', json=study)
    assert rsp.status_code == 404

    # skipping a version when updating an object shouldn't work
    study['version'] = 2
    rsp = api_client.patch('/api/private/studies', json=study)
    assert rsp.status_code == 404

    # updating with an incremented version number should work
    study['version'] = 1
    rsp = api_client.patch('/api/private/studies', json=study)
    assert rsp.status_code == 201

    # updating with an old version number shouldn't work
    study['version'] = 0
    rsp = api_client.patch('/api/private/studies', json=study)
    assert rsp.status_code == 404

    # trying to create a study was already updated shouldn't work
    study['version'] = 0
    rsp = api_client.post('/api/private/studies', json=study)
    assert rsp.status_code == 409

def test_update_study_not_created(api_client: TestClient, uuid: str):
    for i in range(2):
        study = {
            "uuid": uuid,
            "version": i,
            'accession_id': uuid,
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
        rsp = api_client.patch('/api/private/studies', json=study)
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

    rsp = api_client.patch('/api/private/studies', json=existing_study)
    assert rsp.status_code == 201

    study = api_client.get(f'/api/studies/{existing_study["uuid"]}').json()
    assert study["authors"] == new_authors_list
    assert study["title"] == new_title
    assert study["version"] == 1
    assert study["uuid"] == existing_study["uuid"]

    # check changed that shouldn't
    for attr in ["authors", "title", "version"]:
        del study[attr]
        del existing_study[attr]
    assert study == existing_study

def test_update_study_children_counts(api_client: TestClient, existing_study):
    assert existing_study['file_references_count'] == 0

    make_file_references(api_client, existing_study, 10)
    make_images(api_client, existing_study, 5)
    rsp = api_client.post(f"/api/private/studies/{existing_study['uuid']}/refresh_counts")
    assert rsp.status_code, 201

    existing_study = get_study(api_client, existing_study['uuid'])
    assert existing_study['file_references_count'] == 10
    assert existing_study['images_count'] == 5

def test_search_studies_fetch_all(api_client: TestClient):
    # workaround for not starting with a clean db
    rsp = api_client.get(f"/api/search/studies?limit={1000}")
    assert rsp.status_code == 200
    initial_studies_count = len(rsp.json())
    assert initial_studies_count

    for _ in range(5):
        make_study(api_client)
    
    rsp = api_client.get(f"/api/search/studies?limit={1000}")
    assert rsp.status_code == 200
    assert len(rsp.json()) - initial_studies_count == 5
