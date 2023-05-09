from fastapi.testclient import TestClient
from .util import *
import itertools

def test_create_images(api_client: TestClient, existing_study: dict):
    uuids = [get_uuid() for _ in range(2)]
    
    images = [
        {
            "uuid": uuid,
            "version": 0,
            "study_uuid": existing_study['uuid'],
            "name": f"image_{uuid}",
            "original_relpath": f"/home/test/{uuid}",
            "attributes": {
                "image_uuid": uuid
            }
        }
        for uuid in uuids
    ]
    rsp = api_client.post("/api/private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    for uuid in uuids:
        rsp = api_client.get(f"/api/images/{uuid}")
        assert rsp.status_code == 200

def test_create_images_multiple_errors(api_client: TestClient, existing_study: dict):
    uuids = [get_uuid() for _ in range(10)]

    images = [
        {
            "uuid": uuid,
            "version": 0,
            "study_uuid": existing_study['uuid'],
            "name": f"image_{uuid}",
            "original_relpath": f"/home/test/{uuid}",
            "attributes": {
                "image_uuid": uuid
            }
        }
        for uuid in uuids
    ]
    images[5]['version'] = 2
    # mongo rejects *both* documents that violate an index constraint in a multi-doc insert
    images[7]['uuid'] = images[0]['uuid']
    images[3]['study_uuid'] = "00000000-0000-0000-0000-000000000000"

    rsp = api_client.post("/api/private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    # groupby expects sorted list
    bulk_write_results = rsp.json()['items']
    bulk_write_results.sort(key=lambda e: e['status'])
    bulk_write_results_by_status = {
        status: list(items)
        for status, items in itertools.groupby(bulk_write_results, lambda e: e['status'])
    }
    assert set(bulk_write_results_by_status.keys()) == set([201, 400])
    assert len(bulk_write_results_by_status[201]) == 6
    assert len(bulk_write_results_by_status[400]) == 4

    # check all acknowledged docs were actually persisted
    for write_result in bulk_write_results_by_status[201]:
        written_item_uuid = uuids[write_result['idx_in_request']]
        rsp = api_client.get(f"/api/images/{written_item_uuid}")
        assert rsp.status_code == 200, rsp.json()
    
    # check that failed docs have correct errors
    bulk_write_results_by_status[400] = {
        e['idx_in_request']: e
        for e in bulk_write_results_by_status[400]
    }
    
    assert "E11000 duplicate key error" in bulk_write_results_by_status[400][0]['message']
    assert "E11000 duplicate key error" in bulk_write_results_by_status[400][7]['message']
    assert "Expected version to be 0" in bulk_write_results_by_status[400][5]['message']
    assert "Study does not exist" in bulk_write_results_by_status[400][3]['message']

def test_update_image(api_client: TestClient, existing_image: dict):
    existing_image['version'] = 1
    existing_image['name'] = 'some_other_name'

    rsp = api_client.patch("/api/private/images/single", json=existing_image)
    assert rsp.status_code == 200, rsp.json()

def test_image_change_study_to_existing_study(api_client: TestClient, existing_image: dict):
    existing_image['version'] = 1
    
    other_study=make_study(api_client)
    assert existing_image['study_uuid'] != other_study['uuid']
    existing_image['study_uuid'] = other_study['uuid']

    rsp = api_client.patch("/api/private/images/single", json=existing_image)
    assert rsp.status_code == 200, rsp.json()

def test_image_change_study_to_missing_study(api_client: TestClient, existing_image: dict):
    existing_image['version'] = 1

    other_study_uuid = "00000000-0000-0000-0000-000000000000"
    get_study(api_client, other_study_uuid, assert_status_code=404)
    existing_image['study_uuid'] = other_study_uuid

    rsp = api_client.patch("/api/private/images/single", json=existing_image)
    assert rsp.status_code == 404, rsp.json()
