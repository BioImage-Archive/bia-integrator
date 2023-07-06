from fastapi.testclient import TestClient
from .util import *

def test_create_collection(api_client: TestClient, uuid: str):
    # @TODO: Does deleting a study inside a collection cascade/invalidate the collection/something else?
    
    study_uuids = [
        make_study(api_client)['uuid']
        for _ in range(3)
    ]
    collection = {
        "uuid": uuid,
        "version": 0,
        "name": "test_collection_name",
        "title": "test_collection_title",
        "subtitle": "",
        "study_uuids": study_uuids
    }

    rsp = api_client.post(f"/api/private/collections", json=collection)
    assert rsp.status_code == 201, rsp.json()

def test_fetch_study_as_image(api_client: TestClient, existing_study):
    rsp = api_client.get(f"/api/images/{existing_study['uuid']}")
    assert rsp.status_code == 404

def test_fetch_object_info(api_client: TestClient, uuid: str):
    created_study = make_study(api_client, {'accession_id': uuid})

    #rsp = api_client.get(f"/api/object_info_by_accessions?accessions[]={uuid}")
    rsp = api_client.get(f"/api/object_info_by_accessions", params={
        'accessions': [uuid]
    })
    assert rsp.status_code == 200

    assert len(rsp.json()) == 1

    accession_info = rsp.json()[0]
    assert created_study['uuid'] == accession_info['uuid']

def test_fetch_image_by_alias(api_client: TestClient, existing_study, uuid: str):
    images = make_images(api_client, existing_study, 5, image_template = {
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
        "alias": {
            "name": f"{uuid}_test_1"
        },
        "representations": []
    })

    images[2]["alias"] = {
        "name": f"{uuid}_test_2"
    }

    rsp = api_client.get(f"/api/study/{existing_study['uuid']}/images_by_aliases", params={
        'aliases': [f"{uuid}_test_1", f"{uuid}_test_2"]
    })
    assert rsp.status_code == 200
    assert len(rsp.json()) == 5

# should image aliases be unique?
