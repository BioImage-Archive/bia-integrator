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
            "type": "file",
            "study_uuid": existing_study['uuid'],
            "name": "test",
            "uri": "https://test.com/test",
            "size_in_bytes": 100
        }
        for uuid in uuids
    ]
    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    for uuid in uuids:
        rsp = api_client.get(f"file_references/{uuid}")
        assert rsp.status_code == 200

def test_create_file_references_multiple_errors(api_client: TestClient, existing_study: dict, existing_file_reference: dict):
    """Mostly duplicated w/ test_create_images_multiple_errors
    Individually tested below, but this covers lots of failure modes along with some successful parameters in the same request,
        so tests that partially applied changes (only to items that can be created) work
    """
    uuids = [get_uuid() for _ in range(10)]

    file_references = [
        {
            "uuid": uuid,
            "version": 0,
            "type": "file",
            "study_uuid": existing_study['uuid'],
            "name": uuid,
            "uri": "https://test.com/test",
            "size_in_bytes": 1,
            "attributes": {}
        }
        for uuid in uuids
    ]
    del existing_file_reference['model']
    file_references.append(existing_file_reference)

    file_references[5]['version'] = 2
    file_references[7]['uuid'] = file_references[0]['uuid']
    file_references[3]['study_uuid'] = "00000000-0000-0000-0000-000000000000"

    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    # groupby expects sorted list
    bulk_write_results = rsp.json()['items']
    bulk_write_results.sort(key=lambda e: e['status'])
    bulk_write_results_by_status = {
        status: list(items)
        for status, items in itertools.groupby(bulk_write_results, lambda e: e['status'])
    }
    assert set(bulk_write_results_by_status.keys()) == set([201, 400])
    assert len(bulk_write_results_by_status[201]) == 8
    assert len(bulk_write_results_by_status[400]) == 3

    # check all acknowledged docs were actually persisted
    for write_result in bulk_write_results_by_status[201]:
        doc_expected = file_references[write_result['idx_in_request']]
        rsp = api_client.get(f"file_references/{doc_expected['uuid']}")
        assert rsp.status_code == 200, rsp.json()

        doc_persisted = rsp.json()
        del doc_persisted['model']

        assert doc_persisted == doc_expected
    
    # check all rejected docs are actually missing
    for write_result in bulk_write_results_by_status[400]:
        rejected_item = file_references[write_result['idx_in_request']]
        rsp = api_client.get(f"file_references/{rejected_item['uuid']}")

        if "E11000 duplicate key error" in write_result['message']:
            # these do exist, except not in the version they were written in now
            assert rsp.status_code == 200

            # don't just assert on != because it will always pass if model changes
            existing_item = rsp.json()
            existing_item_shaped_as_rejected = {
                k: existing_item[k]
                for k in rejected_item.keys()
            }
            assert rejected_item != existing_item_shaped_as_rejected
        else:
            assert rsp.status_code == 404, rsp.json()
    
    # check that failed docs have correct errors
    bulk_write_results_by_status[400] = {
        e['idx_in_request']: e
        for e in bulk_write_results_by_status[400]
    }
    
    assert "E11000 duplicate key error" in bulk_write_results_by_status[400][7]['message']
    assert "Expected version to be 0" in bulk_write_results_by_status[400][5]['message']
    assert "Study does not exist" in bulk_write_results_by_status[400][3]['message']

def test_create_file_references_existing_unchaged(api_client: TestClient, existing_study: dict, existing_file_reference: dict):
    # adds a file reference but pushes both, second one should get acked
    file_references = [
        get_template_file_reference(existing_study, add_uuid=True)
    ]
    file_references.append(existing_file_reference)

    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201'}, create_result

    assert_bulk_response_items_correct(
        api_client,
        file_references,
        create_result,
        f"file_references"
    )

def test_create_file_references_existing_changed(api_client: TestClient, existing_study: dict, existing_file_reference: dict):
    # change existing filered, should get rejected
    file_references = [
        get_template_file_reference(existing_study, add_uuid=True)
    ]
    file_references.append(existing_file_reference)
    file_references[1]['uri'] += "_only_in_test_object"

    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201', '400'}, create_result
    assert create_result['item_idx_by_status']['201'] == [0] # attempt to create identical existing object ignored
    assert create_result['item_idx_by_status']['400'] == [1] # the updated existing item should fail

    assert_bulk_response_items_correct(
        api_client,
        file_references,
        create_result,
        f"file_references"
    )

def test_create_file_references_missing_study(api_client: TestClient, existing_study: dict):
    file_references = [
        get_template_file_reference(existing_study, add_uuid=True)
        for _ in range(2)
    ]
    file_references[1]['study_uuid'] = "00000000-0000-0000-0000-000000000000"

    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201', '400'}, create_result
    assert create_result['item_idx_by_status']['201'] == [0]
    assert create_result['item_idx_by_status']['400'] == [1]

    assert_bulk_response_items_correct(
        api_client,
        file_references,
        create_result,
        f"file_references"
    )

def test_create_file_references_nonzero_version(api_client: TestClient, existing_study: dict):
    file_references = [
        get_template_file_reference(existing_study, add_uuid=True)
        for _ in range(2)
    ]
    file_references[1]['version'] = 1

    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201', '400'}, create_result
    assert create_result['item_idx_by_status']['201'] == [0]
    assert create_result['item_idx_by_status']['400'] == [1]

    assert_bulk_response_items_correct(
        api_client,
        file_references,
        create_result,
        f"file_references"
    )

def test_create_file_references_same_request_duplicates(api_client: TestClient, existing_study: dict):
    # always check that the failures are partial, i.e. the things that are correct do actually get created
    file_references = [
        get_template_file_reference(existing_study, add_uuid=True)
        for _ in range(2)
    ]
    file_references.append(file_references[1])

    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201'}, create_result
    assert create_result['item_idx_by_status']['201'] == [0, 1, 2]

    assert_bulk_response_items_correct(
        api_client,
        file_references,
        create_result,
        f"file_references"
    )

def test_create_file_references_same_request_almost_duplicates(api_client: TestClient, existing_study: dict):
    # duplicate, except for fields that don't have uniqueness constraints
    # always check that the failures are partial, i.e. the things that are correct do actually get created
    file_references = [
        get_template_file_reference(existing_study, add_uuid=True)
        for _ in range(2)
    ]
    almost_duplicate_fileref = file_references[1].copy()
    almost_duplicate_fileref['uri'] += "_only_in_test_object"
    file_references.append(almost_duplicate_fileref)

    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201', '400'}, create_result
    assert create_result['item_idx_by_status']['201'] == [0, 1]
    assert create_result['item_idx_by_status']['400'] == [2]

    # things that can be created, should be created in a batch op
    assert create_result['items'][0]['status'] == 201
    assert api_client.get(f"file_references/{file_references[0]['uuid']}").status_code == 200

    # This is the main point of the test!
    #   if a bulk create request attempts to create two (or more) conflicting items,
    #   then only the 1st item (in the conflicting subset) is created
    assert create_result['items'][1]['status'] == 201
    assert create_result['items'][2]['status'] == 400

    rsp = api_client.get(f"file_references/{file_references[1]['uuid']}")
    assert rsp.status_code == 200

    file_reference_created = rsp.json()
    assert file_reference_created == file_references[1]
    assert file_reference_created != file_references[2]

def test_create_file_references_idempotent_on_identical_ops_when_defaults_missing(api_client: TestClient, existing_study: dict, existing_file_reference: dict):
    existing_file_reference_without_default_field = existing_file_reference.copy()
    
    del existing_file_reference_without_default_field['attributes']
    del existing_file_reference_without_default_field['model']
    # just in case the default existing_file_reference gets changed
    assert existing_file_reference_without_default_field != existing_file_reference

    file_references = [
        existing_file_reference,
        existing_file_reference_without_default_field
    ]
    rsp = api_client.post("private/file_references", json=file_references)
    assert rsp.status_code == 201, rsp.json()
    rsp = rsp.json()
    # This would pass anyway since it's identical to an existing fileref
    assert rsp['items'][0]['status'] == 201

    # This should pass even if not identical to an existing fileref, since it becomes identical after adding model defaults
    assert rsp['items'][1]['status'] == 201

def test_update_file_reference(api_client: TestClient, existing_file_reference: dict):
    existing_file_reference['version'] = 1
    existing_file_reference['name'] = 'some_other_name'

    rsp = api_client.patch("private/file_references/single", json=existing_file_reference)
    assert rsp.status_code == 200, rsp.json()

def test_file_reference_pagination_defaults(api_client: TestClient, existing_study: dict):
    file_references = make_file_references(api_client, existing_study, 100)
    file_references.sort(key=lambda img: UUID(img['uuid']).hex)

    rsp = api_client.get(f"studies/{existing_study['uuid']}/file_references")
    assert rsp.status_code == 200
    file_references_fetched = rsp.json()

    assert len(file_references_fetched) == 10
    assert file_references[:10] == file_references_fetched

def test_file_reference_pagination(api_client: TestClient, existing_study: dict):
    file_references = make_file_references(api_client, existing_study, 5)
    file_references.sort(key=lambda img: UUID(img['uuid']).hex)
    chunk_size = 2

    #1,2
    rsp = api_client.get(f"studies/{existing_study['uuid']}/file_references?limit={chunk_size}")
    assert rsp.status_code == 200
    file_references_fetched = rsp.json()

    assert len(file_references_fetched) == chunk_size
    images_chunk = file_references[:2]
    assert images_chunk == file_references_fetched

    #3,4
    rsp = api_client.get(f"studies/{existing_study['uuid']}/file_references?start_uuid={file_references_fetched[-1]['uuid']}&limit={chunk_size}")
    assert rsp.status_code == 200
    file_references_fetched = rsp.json()

    assert len(file_references_fetched) == chunk_size
    images_chunk = file_references[2:4]
    assert images_chunk == file_references_fetched

    #5
    rsp = api_client.get(f"studies/{existing_study['uuid']}/file_references?start_uuid={file_references_fetched[-1]['uuid']}&limit={chunk_size}")
    assert rsp.status_code == 200
    file_references_fetched = rsp.json()

    assert len(file_references_fetched) == 1
    images_chunk = file_references[4:5]
    assert images_chunk == file_references_fetched

def test_file_reference_large_page(api_client: TestClient, existing_study: dict):
    file_references = make_file_references(api_client, existing_study, 5)
    file_references.sort(key=lambda img: UUID(img['uuid']).hex)

    rsp = api_client.get(f"studies/{existing_study['uuid']}/file_references?limit={10000}")
    assert rsp.status_code == 200
    file_references_fetched = rsp.json()

    assert len(file_references_fetched) == 5
    assert file_references == file_references_fetched

def test_file_reference_pagination_bad_limit(api_client: TestClient, existing_study: dict):
    file_references = make_file_references(api_client, existing_study, 5)
    file_references.sort(key=lambda img: UUID(img['uuid']).hex)

    rsp = api_client.get(f"studies/{existing_study['uuid']}/file_references?limit={0}")
    assert rsp.status_code == 422
