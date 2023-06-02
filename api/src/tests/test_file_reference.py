from fastapi.testclient import TestClient
from .util import *
import itertools
from uuid import UUID

def test_create_file_references(api_client: TestClient, existing_study: dict):
    uuids = [get_uuid() for _ in range(2)]
    
    file_references = [
        {
            "uuid": uuid,
            "version": 0,
            "accession_id": f"test-{uuid}",
            "type": "file",
            "study_uuid": existing_study['uuid'],
            "name": "test",
            "uri": "https://test.com/test"
        }
        for uuid in uuids
    ]
    rsp = api_client.post("/api/private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    for uuid in uuids:
        rsp = api_client.get(f"/api/file_references/{uuid}")
        assert rsp.status_code == 200

def test_create_file_references_multiple_errors(api_client: TestClient, existing_study: dict):
    """Mostly duplicated w/ test_create_images_multiple_errors
    @TODO: generic way to verity errors in buk responses?"""
    uuids = [get_uuid() for _ in range(10)]

    file_references = [
        {
            "uuid": uuid,
            "version": 0,
            "accession_id": f"test-{uuid}",
            "type": "file",
            "study_uuid": existing_study['uuid'],
            "name": "test",
            "uri": "https://test.com/test"
        }
        for uuid in uuids
    ]

    file_references[5]['version'] = 2
    # mongo rejects *both* documents that violate an index constraint in a multi-doc insert
    file_references[7]['uuid'] = file_references[0]['uuid']
    file_references[3]['study_uuid'] = "00000000-0000-0000-0000-000000000000"

    rsp = api_client.post("/api/private/file_references", json=file_references)
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
        rsp = api_client.get(f"/api/file_references/{written_item_uuid}")
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

def test_update_file_reference(api_client: TestClient, existing_file_reference: dict):
    existing_file_reference['version'] = 1
    existing_file_reference['name'] = 'some_other_name'

    rsp = api_client.patch("/api/private/file_references/single", json=existing_file_reference)
    assert rsp.status_code == 200, rsp.json()

def test_file_reference_pagination_defaults(api_client: TestClient, existing_study: dict):
    file_references = make_file_references(api_client, existing_study, 100)
    file_references.sort(key=lambda img: UUID(img['uuid']).hex)

    rsp = api_client.get(f"/api/{existing_study['uuid']}/file_references")
    assert rsp.status_code == 200
    file_references_fetched = rsp.json()
    for file_ref in file_references_fetched:
        del file_ref['_id']
        del file_ref['model']

    assert len(file_references_fetched) == 10
    assert file_references[:10] == file_references_fetched

def test_file_reference_pagination(api_client: TestClient, existing_study: dict):
    file_references = make_file_references(api_client, existing_study, 5)
    file_references.sort(key=lambda img: UUID(img['uuid']).hex)
    chunk_size = 2

    #1,2
    rsp = api_client.get(f"/api/{existing_study['uuid']}/file_references?limit={chunk_size}")
    assert rsp.status_code == 200
    file_references_fetched = rsp.json()
    for file_ref in file_references_fetched:
        del file_ref['_id']
        del file_ref['model']
    assert len(file_references_fetched) == chunk_size
    images_chunk = file_references[:2]
    assert images_chunk == file_references_fetched

    #3,4
    rsp = api_client.get(f"/api/{existing_study['uuid']}/file_references?start_uuid={file_references_fetched[-1]['uuid']}&limit={chunk_size}")
    assert rsp.status_code == 200
    file_references_fetched = rsp.json()
    for file_ref in file_references_fetched:
        del file_ref['_id']
        del file_ref['model']
    assert len(file_references_fetched) == chunk_size
    images_chunk = file_references[2:4]
    assert images_chunk == file_references_fetched

    #5
    rsp = api_client.get(f"/api/{existing_study['uuid']}/file_references?start_uuid={file_references_fetched[-1]['uuid']}&limit={chunk_size}")
    assert rsp.status_code == 200
    file_references_fetched = rsp.json()
    for file_ref in file_references_fetched:
        del file_ref['_id']
        del file_ref['model']
    assert len(file_references_fetched) == 1
    images_chunk = file_references[4:5]
    assert images_chunk == file_references_fetched

def test_file_reference_large_page(api_client: TestClient, existing_study: dict):
    file_references = make_file_references(api_client, existing_study, 5)
    file_references.sort(key=lambda img: UUID(img['uuid']).hex)

    rsp = api_client.get(f"/api/{existing_study['uuid']}/file_references?limit={10000}")
    assert rsp.status_code == 200
    file_references_fetched = rsp.json()
    for file_ref in file_references_fetched:
        del file_ref['_id']
        del file_ref['model']
    assert len(file_references_fetched) == 5
    assert file_references == file_references_fetched

def test_file_reference_pagination_bad_limit(api_client: TestClient, existing_study: dict):
    file_references = make_file_references(api_client, existing_study, 5)
    file_references.sort(key=lambda img: UUID(img['uuid']).hex)

    rsp = api_client.get(f"/api/{existing_study['uuid']}/file_references?limit={0}")
    assert rsp.status_code == 422
