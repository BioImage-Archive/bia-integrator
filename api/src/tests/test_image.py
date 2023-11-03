from fastapi.testclient import TestClient
from .util import *
import itertools
from uuid import UUID
import os

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
    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    for uuid in uuids:
        rsp = api_client.get(f"images/{uuid}")
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
    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    for uuid in uuids:
        rsp = api_client.get(f"images/{uuid}")
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

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    # groupby expects sorted list
    bulk_write_results = rsp.json()['items']
    bulk_write_results.sort(key=lambda e: e['status'])
    bulk_write_results_by_status = {
        status: list(items)
        for status, items in itertools.groupby(bulk_write_results, lambda e: e['status'])
    }
    assert set(bulk_write_results_by_status.keys()) == set([201, 400])
    assert len(bulk_write_results_by_status[201]) == 7
    assert len(bulk_write_results_by_status[400]) == 3

    # check all acknowledged docs were actually persisted
    for write_result in bulk_write_results_by_status[201]:
        written_item_uuid = uuids[write_result['idx_in_request']]
        rsp = api_client.get(f"images/{written_item_uuid}")
        assert rsp.status_code == 200, rsp.json()
    
    # check that failed docs have correct errors
    bulk_write_results_by_status[400] = {
        e['idx_in_request']: e
        for e in bulk_write_results_by_status[400]
    }
    
    assert "E11000 duplicate key error" in bulk_write_results_by_status[400][7]['message']
    assert "Expected version to be 0" in bulk_write_results_by_status[400][5]['message']
    assert "Study does not exist" in bulk_write_results_by_status[400][3]['message']


def test_create_images_existing_unchaged(api_client: TestClient, existing_study: dict, existing_image: dict):
    # adds a file reference but pushes both, second one should get acked
    images = [
        get_template_image(existing_study, add_uuid=True)
    ]
    images.append(existing_image)

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201'}, create_result

    assert_bulk_response_items_correct(
        api_client,
        images,
        create_result,
        f"images"
    )

def test_create_images_existing_changed(api_client: TestClient, existing_study: dict, existing_image: dict):
    # change existing filered, should get rejected
    images = [
        get_template_image(existing_study, add_uuid=True)
    ]
    images.append(existing_image)
    images[1]['dimensions'] = "only_in_test_object"

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201', '400'}, create_result
    assert create_result['item_idx_by_status']['201'] == [0] # attempt to create identical existing object ignored
    assert create_result['item_idx_by_status']['400'] == [1] # the updated existing item should fail

    assert_bulk_response_items_correct(
        api_client,
        images,
        create_result,
        f"images"
    )

def test_create_images_missing_study(api_client: TestClient, existing_study: dict):
    images = [
        get_template_image(existing_study, add_uuid=True)
        for _ in range(2)
    ]
    images[1]['study_uuid'] = "00000000-0000-0000-0000-000000000000"

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201', '400'}, create_result
    assert create_result['item_idx_by_status']['201'] == [0]
    assert create_result['item_idx_by_status']['400'] == [1]

    assert_bulk_response_items_correct(
        api_client,
        images,
        create_result,
        f"images"
    )

def test_create_images_nonzero_version(api_client: TestClient, existing_study: dict):
    images = [
        get_template_image(existing_study, add_uuid=True)
        for _ in range(2)
    ]
    images[1]['version'] = 1

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201', '400'}, create_result
    assert create_result['item_idx_by_status']['201'] == [0]
    assert create_result['item_idx_by_status']['400'] == [1]

    assert_bulk_response_items_correct(
        api_client,
        images,
        create_result,
        f"images"
    )

def test_create_images_same_request_duplicates(api_client: TestClient, existing_study: dict):
    # always check that the failures are partial, i.e. the things that are correct do actually get created
    images = [
        get_template_image(existing_study, add_uuid=True)
        for _ in range(2)
    ]
    images.append(images[1])

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201'}, create_result
    assert create_result['item_idx_by_status']['201'] == [0, 1, 2]

    assert_bulk_response_items_correct(
        api_client,
        images,
        create_result,
        f"images"
    )

def test_create_images_same_request_almost_duplicates(api_client: TestClient, existing_study: dict):
    # duplicate, except for fields that don't have uniqueness constraints
    # always check that the failures are partial, i.e. the things that are correct do actually get created
    images = [
        get_template_image(existing_study, add_uuid=True)
        for _ in range(2)
    ]
    almost_duplicate_image = images[1].copy()
    almost_duplicate_image['dimensions'] = "only_in_test_object"
    images.append(almost_duplicate_image)

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result['item_idx_by_status'].keys()) == {'201', '400'}, create_result
    assert create_result['item_idx_by_status']['201'] == [0, 1]
    assert create_result['item_idx_by_status']['400'] == [2]

    # things that can be created, should be created in a batch op
    assert create_result['items'][0]['status'] == 201
    assert api_client.get(f"images/{images[0]['uuid']}").status_code == 200

    # This is the main point of the test!
    #   if a bulk create request attempts to create two (or more) conflicting items,
    #   then only the 1st item (in the conflicting subset) is created
    assert create_result['items'][1]['status'] == 201
    assert create_result['items'][2]['status'] == 400

    rsp = api_client.get(f"images/{images[1]['uuid']}")
    assert rsp.status_code == 200

    image_created = rsp.json()
    assert image_created == images[1]
    assert image_created != images[2]

def test_create_images_idempotent_on_identical_ops_when_defaults_missing(api_client: TestClient, existing_study: dict, existing_image: dict):
    existing_image_without_default_field = existing_image.copy()
    
    del existing_image_without_default_field['annotations']
    del existing_image_without_default_field['model']
    # just in case the default existing_image gets changed
    assert existing_image_without_default_field != existing_image

    images = [
        existing_image,
        existing_image_without_default_field
    ]
    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()
    rsp = rsp.json()
    # This would pass anyway since it's identical to an existing image
    assert rsp['items'][0]['status'] == 201

    # This should pass even if not identical to an existing image, since it becomes identical after adding model defaults
    assert rsp['items'][1]['status'] == 201

def test_update_image(api_client: TestClient, existing_image: dict):
    existing_image['version'] = 1
    existing_image['name'] = 'some_other_name'

    rsp = api_client.patch("private/images/single", json=existing_image)
    assert rsp.status_code == 200, rsp.json()

def test_image_change_study_to_existing_study(api_client: TestClient, existing_image: dict):
    existing_image['version'] = 1
    
    other_study=make_study(api_client)
    assert existing_image['study_uuid'] != other_study['uuid']
    existing_image['study_uuid'] = other_study['uuid']

    rsp = api_client.patch("private/images/single", json=existing_image)
    assert rsp.status_code == 200, rsp.json()

def test_image_change_study_to_missing_study(api_client: TestClient, existing_image: dict):
    existing_image['version'] = 1

    other_study_uuid = "00000000-0000-0000-0000-000000000000"
    get_study(api_client, other_study_uuid, assert_status_code=404)
    existing_image['study_uuid'] = other_study_uuid

    rsp = api_client.patch("private/images/single", json=existing_image)
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
    rsp = api_client.post(f"private/images/{existing_image['uuid']}/representations/single", json=representation)
    assert rsp.status_code == 201, rsp.json()

def test_add_image_representation_missing_image(api_client: TestClient, existing_study: dict):
    representation = {
        "accession_id": "test-representation",
        "size": 1
    }
    rsp = api_client.post(f"private/images/00000000-0000-0000-0000-000000000000/representations/single", json=representation)
    assert rsp.status_code == 404, rsp.json()

def test_study_with_images_and_filerefs_fetch_images(api_client: TestClient, existing_study: dict):
    """
    Images and filerefs go through the same code path mostly but are different. Check they are filtered properly
    Initially found as a bug
    """
    images = make_images(api_client, existing_study, 2)
    images_created = set([img['uuid'] for img in images])
    make_file_references(api_client, existing_study, 2)

    rsp = api_client.get(f"studies/{existing_study['uuid']}/images")
    assert rsp.status_code == 200
    images_fetched = set([img['uuid'] for img in rsp.json()])
    assert images_fetched == images_created

def test_image_pagination(api_client: TestClient, existing_study: dict):
    images = make_images(api_client, existing_study, 5)
    images.sort(key=lambda img: UUID(img['uuid']).hex)
    chunk_size = 2

    #1,2
    rsp = api_client.get(f"studies/{existing_study['uuid']}/images?limit={chunk_size}")
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    assert len(images_fetched) == chunk_size
    images_chunk = images[:2]
    assert images_chunk[0] == images_fetched[0]

    #3,4
    rsp = api_client.get(f"studies/{existing_study['uuid']}/images?start_uuid={images_fetched[-1]['uuid']}&limit={chunk_size}")
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    assert len(images_fetched) == chunk_size
    images_chunk = images[2:4]
    assert images_chunk == images_fetched

    #5
    rsp = api_client.get(f"studies/{existing_study['uuid']}/images?start_uuid={images_fetched[-1]['uuid']}&limit={chunk_size}")
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    assert len(images_fetched) == 1
    images_chunk = images[4:5]
    assert images_chunk == images_fetched

def test_image_pagination_large_page(api_client: TestClient, existing_study: dict):
    images = make_images(api_client, existing_study, 5)
    images.sort(key=lambda img: UUID(img['uuid']).hex)

    rsp = api_client.get(f"studies/{existing_study['uuid']}/images?limit={10000}")
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    assert len(images_fetched) == 5
    assert images == images_fetched

def test_image_pagination_bad_limit(api_client: TestClient, existing_study: dict):
    images = make_images(api_client, existing_study, 5)
    images.sort(key=lambda img: UUID(img['uuid']).hex)

    rsp = api_client.get(f"studies/{existing_study['uuid']}/images?limit={0}")
    assert rsp.status_code == 422

def test_image_ome_metadata_create_get(api_client: TestClient, existing_image: dict):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(script_dir, "data/simple.ome.xml")) as f:
        rsp = api_client.post(f"private/images/{existing_image['uuid']}/ome_metadata", files={"ome_metadata_file": f.read()})
        assert rsp.status_code == 201

        bia_image_ome_metadata = rsp.json()
        assert bia_image_ome_metadata['bia_image_uuid'] == existing_image['uuid']
        assert bia_image_ome_metadata['ome_metadata']['images'][0]['name'] == "XY-ch-02"

    rsp = api_client.get(f"images/{existing_image['uuid']}/ome_metadata")
    assert rsp.status_code == 200
    bia_image_ome_metadata = rsp.json()
    assert bia_image_ome_metadata['bia_image_uuid'] == existing_image['uuid']
    assert bia_image_ome_metadata['ome_metadata']['images'][0]['name'] == "XY-ch-02"

def test_post_invalid_ome_metadata(api_client: TestClient, existing_image: dict):
    with open(os.path.realpath(__file__)) as f:
        rsp = api_client.post(f"private/images/{existing_image['uuid']}/ome_metadata", files={"ome_metadata_file": f.read()})
        assert rsp.status_code == 500

    # check no ome metadata object was created
    rsp = api_client.get(f"images/{existing_image['uuid']}/ome_metadata")
    assert rsp.status_code == 404

def test_image_ome_metadata_update(api_client: TestClient, existing_image: dict):
    script_dir = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(script_dir, "data/simple.ome.xml")) as f:
        rsp = api_client.post(f"private/images/{existing_image['uuid']}/ome_metadata", files={"ome_metadata_file": f.read()})
        assert rsp.status_code == 201
    with open(os.path.join(script_dir, "data/simple.ome.xml")) as f:
        rsp = api_client.post(f"private/images/{existing_image['uuid']}/ome_metadata", files={"ome_metadata_file": f.read()})
        assert rsp.status_code == 201

    rsp = api_client.get(f"images/{existing_image['uuid']}/ome_metadata")
    assert rsp.status_code == 200
