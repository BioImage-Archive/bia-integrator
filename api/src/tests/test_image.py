from fastapi.testclient import TestClient
from .util import *
import itertools
from uuid import UUID

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

def test_image_annotations_applied(api_client: TestClient, existing_study: dict):
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
            },
            "annotations": [{
                "author_email": "test@ebi.ac.uk",
                "key": "custom_annotation",
                "value": "should_only_be_added_as_an_attribute",
                "state": "active"
            }, {
                "author_email": "test@ebi.ac.uk",
                "key": "original_relpath",
                "value": "this/should/overwrite/original",
                "state": "active"
            }]
        }
        for uuid in uuids
    ]
    rsp = api_client.post("/api/private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    for uuid in uuids:
        rsp = api_client.get(f"/api/images/{uuid}")
        assert rsp.status_code == 200
        img = rsp.json()

        assert img['attributes']['image_uuid'] is not None
        assert img['attributes']['custom_annotation'] == "should_only_be_added_as_an_attribute"
        assert img['original_relpath'] == "this/should/overwrite/original"

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

def test_add_image_representation(api_client: TestClient, existing_image: dict):
    """
    Would rather not add uuids for sub-objects because then we need to define what a sub-object is.
    Also, deleting/updating (a.i. the uncommon situations) don't make sense until we can identify specific sub-objects, allowing for parallel request
    So just don't support either (a.i. to delete a representation, modify the parent image instead of using an endpoint for this purpose only)
    Adding new representations works as a separate operation"""

    representation = {
        "size": 1
    }
    rsp = api_client.post(f"/api/private/images/{existing_image['uuid']}/representations/single", json=representation)
    assert rsp.status_code == 201, rsp.json()

def test_add_image_representation_missing_image(api_client: TestClient, existing_study: dict):
    representation = {
        "accession_id": "test-representation",
        "size": 1
    }
    rsp = api_client.post(f"/api/private/images/00000000-0000-0000-0000-000000000000/representations/single", json=representation)
    assert rsp.status_code == 404, rsp.json()

def test_study_with_images_and_filerefs_fetch_images(api_client: TestClient, existing_study: dict):
    """
    Images and filerefs go through the same code path mostly but are different. Check they are filtered properly
    Initially found as a bug
    """
    images = make_images(api_client, existing_study, 2)
    images_created = set([img['uuid'] for img in images])
    make_file_references(api_client, existing_study, 2)

    rsp = api_client.get(f"/api/studies/{existing_study['uuid']}/images")
    assert rsp.status_code == 200
    images_fetched = set([img['uuid'] for img in rsp.json()])
    assert images_fetched == images_created

def test_image_pagination(api_client: TestClient, existing_study: dict):
    images = make_images(api_client, existing_study, 5)
    images.sort(key=lambda img: UUID(img['uuid']).hex)
    chunk_size = 2

    #1,2
    rsp = api_client.get(f"/api/studies/{existing_study['uuid']}/images?limit={chunk_size}")
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    for img in images_fetched:
        del img['model']
    assert len(images_fetched) == chunk_size
    images_chunk = images[:2]
    assert images_chunk == images_fetched

    #3,4
    rsp = api_client.get(f"/api/studies/{existing_study['uuid']}/images?start_uuid={images_fetched[-1]['uuid']}&limit={chunk_size}")
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    for img in images_fetched:
        del img['model']
    assert len(images_fetched) == chunk_size
    images_chunk = images[2:4]
    assert images_chunk == images_fetched

    #5
    rsp = api_client.get(f"/api/studies/{existing_study['uuid']}/images?start_uuid={images_fetched[-1]['uuid']}&limit={chunk_size}")
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    for img in images_fetched:
        del img['model']
    assert len(images_fetched) == 1
    images_chunk = images[4:5]
    assert images_chunk == images_fetched

def test_image_pagination_large_page(api_client: TestClient, existing_study: dict):
    images = make_images(api_client, existing_study, 5)
    images.sort(key=lambda img: UUID(img['uuid']).hex)

    rsp = api_client.get(f"/api/studies/{existing_study['uuid']}/images?limit={10000}")
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    for img in images_fetched:
        del img['model']
    assert len(images_fetched) == 5
    assert images == images_fetched

def test_image_pagination_bad_limit(api_client: TestClient, existing_study: dict):
    images = make_images(api_client, existing_study, 5)
    images.sort(key=lambda img: UUID(img['uuid']).hex)

    rsp = api_client.get(f"/api/studies/{existing_study['uuid']}/images?limit={0}")
    assert rsp.status_code == 422
