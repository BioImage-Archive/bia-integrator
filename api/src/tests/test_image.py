from fastapi.testclient import TestClient
import pytest
from typing import List
from .util import (
    get_uuid,
    make_file_references,
    make_images,
    make_study,
    get_study,
    get_template_image,
    unorderd_lists_equality,
    assert_bulk_response_items_correct,
    package_base,
)
import itertools
from uuid import UUID
import os


def create_image_list(
    image_count: int, existing_study: dict
) -> tuple[list[str], list[dict]]:
    uuids = [get_uuid() for _ in range(image_count)]

    images = [
        {
            "uuid": uuid,
            "version": 0,
            "study_uuid": existing_study["uuid"],
            "name": f"image_{uuid}",
            "original_relpath": f"/home/test/{uuid}",
            "attributes": {
                "image_uuid": uuid,
            },
        }
        for uuid in uuids
    ]

    return uuids, images


def test_create_images_valid(
    api_client: TestClient, existing_study: dict, existing_image_acquisition: dict
):

    uuids, images = create_image_list(2, existing_study)
    images[1]["image_acquisitions_uuid"] = [existing_image_acquisition["uuid"]]
    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 201, rsp.json()

    for uuid in uuids:
        rsp = api_client.get(f"images/{uuid}")
        assert rsp.status_code == 200


def test_create_images_multiple_errors(
    api_client: TestClient,
    existing_study: dict,
    existing_specimen: dict,
    existing_image_acquisition: dict,
):
    uuids, images = create_image_list(10, existing_study)

    images[4]["version"] = 2
    # mongo rejects *both* documents that violate an index constraint in a multi-doc insert
    images[5]["uuid"] = images[0]["uuid"]
    images[6]["study_uuid"] = "00000000-0000-0000-0000-000000000000"
    images[7]["study_uuid"] = existing_specimen["uuid"]
    images[8]["image_acquisitions_uuid"] = [existing_image_acquisition["uuid"]]
    images[9]["study_uuid"] = existing_image_acquisition["uuid"]

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 400, rsp.json()

    # groupby expects sorted list
    bulk_write_results = rsp.json()["items"]
    bulk_write_results.sort(key=lambda e: e["status"])
    bulk_write_results_by_status = {
        status: list(items)
        for status, items in itertools.groupby(
            bulk_write_results, lambda e: e["status"]
        )
    }
    assert set(bulk_write_results_by_status.keys()) == set([201, 400])
    assert len(bulk_write_results_by_status[201]) == 4
    assert len(bulk_write_results_by_status[400]) == 6

    # check all acknowledged docs were actually persisted
    for write_result in bulk_write_results_by_status[201]:
        written_item_uuid = uuids[write_result["idx_in_request"]]
        rsp = api_client.get(f"images/{written_item_uuid}")
        assert rsp.status_code == 200, rsp.json()

    # check that failed docs have correct errors
    bulk_write_results_by_status[400] = {
        e["idx_in_request"]: e for e in bulk_write_results_by_status[400]
    }

    assert "Expected version to be 0" in bulk_write_results_by_status[400][4]["message"]
    assert (
        "E11000 duplicate key error" in bulk_write_results_by_status[400][5]["message"]
    )
    assert (
        f"{images[6]['study_uuid']} does not exist"
        in bulk_write_results_by_status[400][6]["message"]
    )
    assert (
        f"{images[7]['study_uuid']} expected to be of type BIAStudy, but found Specimen"
        in bulk_write_results_by_status[400][7]["message"]
    )
    # Check that 2 different images using the same image_acquisition uuid for an image acquisition and a study both get an error message.
    assert (
        f"Your request expects {images[9]['study_uuid']} to be an instance of more than 1 of conflicting types: BIAStudy, ImageAcquisition, when it is an instance of ImageAcquisition."
        in bulk_write_results_by_status[400][8]["message"]
    )
    assert (
        f"Your request expects {images[9]['study_uuid']} to be an instance of more than 1 of conflicting types: BIAStudy, ImageAcquisition, when it is an instance of ImageAcquisition."
        in bulk_write_results_by_status[400][9]["message"]
    )


def test_create_images_existing_unchaged(
    api_client: TestClient, existing_study: dict, existing_image: dict
):
    # adds a file reference but pushes both, second one should get acked
    images = [
        get_template_image(existing_study, add_uuid=True),
    ]
    images.append(existing_image)

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 400, rsp.json()

    rsp = api_client.post(
        "private/images", json=images, params=[("overwrite_mode", "allow_idempotent")]
    )
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result["item_idx_by_status"].keys()) == {"201"}, create_result

    assert_bulk_response_items_correct(api_client, images, create_result, f"images")


def test_create_images_existing_changed(
    api_client: TestClient, existing_study: dict, existing_image: dict
):
    # change existing filered, should get rejected
    images = [
        get_template_image(existing_study, add_uuid=True),
    ]
    images.append(existing_image)
    images[1]["dimensions"] = "only_in_test_object"

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 400, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result["item_idx_by_status"].keys()) == {
        "201",
        "400",
    }, create_result
    assert create_result["item_idx_by_status"]["201"] == [
        0
    ]  # attempt to create identical existing object ignored
    assert create_result["item_idx_by_status"]["400"] == [
        1
    ]  # the updated existing item should fail

    assert_bulk_response_items_correct(api_client, images, create_result, f"images")


def test_create_images_missing_study(api_client: TestClient, existing_study: dict):
    images = [get_template_image(existing_study, add_uuid=True) for _ in range(2)]
    images[1]["study_uuid"] = "00000000-0000-0000-0000-000000000000"

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 400, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result["item_idx_by_status"].keys()) == {
        "201",
        "400",
    }, create_result
    assert create_result["item_idx_by_status"]["201"] == [0]
    assert create_result["item_idx_by_status"]["400"] == [1]

    assert_bulk_response_items_correct(api_client, images, create_result, f"images")


def test_create_images_nonzero_version(api_client: TestClient, existing_study: dict):
    images = [get_template_image(existing_study, add_uuid=True) for _ in range(2)]
    images[1]["version"] = 1

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 400, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result["item_idx_by_status"].keys()) == {
        "201",
        "400",
    }, create_result
    assert create_result["item_idx_by_status"]["201"] == [0]
    assert create_result["item_idx_by_status"]["400"] == [1]

    assert_bulk_response_items_correct(api_client, images, create_result, f"images")


def test_create_images_same_request_duplicates(
    api_client: TestClient, existing_study: dict
):
    # always check that the failures are partial, i.e. the things that are correct do actually get created
    images = [get_template_image(existing_study, add_uuid=True) for _ in range(2)]
    images.append(images[1])

    # duplicates should fail without the idempotent flag set
    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 400, rsp.json()

    # duplicates should fail without the idempotent flag set
    rsp = api_client.post(
        "private/images", json=images, params=[("overwrite_mode", "allow_idempotent")]
    )
    assert rsp.status_code == 201, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result["item_idx_by_status"].keys()) == {"201"}, create_result
    assert create_result["item_idx_by_status"]["201"] == [0, 1, 2]

    assert_bulk_response_items_correct(api_client, images, create_result, f"images")


def test_create_images_same_request_almost_duplicates(
    api_client: TestClient, existing_study: dict
):
    # duplicate, except for fields that don't have uniqueness constraints
    # always check that the failures are partial, i.e. the things that are correct do actually get created
    images = [get_template_image(existing_study, add_uuid=True) for _ in range(2)]
    almost_duplicate_image = images[1].copy()
    almost_duplicate_image["dimensions"] = "only_in_test_object"
    images.append(almost_duplicate_image)

    rsp = api_client.post("private/images", json=images)
    assert rsp.status_code == 400, rsp.json()

    create_result = rsp.json()
    # Object attributes can only be strings (from json spec)
    assert set(create_result["item_idx_by_status"].keys()) == {
        "201",
        "400",
    }, create_result
    assert create_result["item_idx_by_status"]["201"] == [0, 1]
    assert create_result["item_idx_by_status"]["400"] == [2]

    # things that can be created, should be created in a batch op
    assert create_result["items"][0]["status"] == 201
    assert api_client.get(f"images/{images[0]['uuid']}").status_code == 200

    # This is the main point of the test!
    #   if a bulk create request attempts to create two (or more) conflicting items,
    #   then only the 1st item (in the conflicting subset) is created
    assert create_result["items"][1]["status"] == 201
    assert create_result["items"][2]["status"] == 400

    rsp = api_client.get(f"images/{images[1]['uuid']}")
    assert rsp.status_code == 200

    image_created = rsp.json()
    assert image_created == images[1]
    assert image_created != images[2]


def test_create_images_idempotent_on_identical_ops_when_defaults_missing(
    api_client: TestClient, existing_study: dict, existing_image: dict
):
    existing_image_without_default_field = existing_image.copy()

    del existing_image_without_default_field["annotations"]
    del existing_image_without_default_field["model"]
    # just in case the default existing_image gets changed
    assert existing_image_without_default_field != existing_image

    images = [
        existing_image,
        existing_image_without_default_field,
    ]
    rsp = api_client.post(
        "private/images", json=images, params=[("overwrite_mode", "allow_idempotent")]
    )
    assert rsp.status_code == 201, rsp.json()
    rsp = rsp.json()
    # This would pass anyway since it's identical to an existing image
    assert rsp["items"][0]["status"] == 201

    # This should pass even if not identical to an existing image, since it becomes identical after adding model defaults
    assert rsp["items"][1]["status"] == 201


def test_update_image(
    api_client: TestClient, existing_image: dict, existing_image_acquisition: dict
):
    existing_image["version"] = 1
    existing_image["name"] = "some_other_name"
    existing_image["image_acquisitions_uuid"] = [existing_image_acquisition["uuid"]]

    rsp = api_client.patch("private/images/single", json=existing_image)
    assert rsp.status_code == 200, rsp.json()


def test_update_image_change_study_to_existing_study(
    api_client: TestClient, existing_image: dict
):
    existing_image["version"] = 1

    other_study = make_study(api_client)
    assert existing_image["study_uuid"] != other_study["uuid"]
    existing_image["study_uuid"] = other_study["uuid"]

    rsp = api_client.patch("private/images/single", json=existing_image)
    assert rsp.status_code == 200, rsp.json()


def test_update_image_change_study_to_missing_study(
    api_client: TestClient, existing_image: dict
):
    existing_image["version"] = 1

    other_study_uuid = "00000000-0000-0000-0000-000000000000"
    get_study(api_client, other_study_uuid, assert_status_code=404)
    existing_image["study_uuid"] = other_study_uuid

    rsp = api_client.patch("private/images/single", json=existing_image)
    assert rsp.status_code == 404, rsp.json()


def test_create_image_representation(api_client: TestClient, existing_image: dict):
    """
    Would rather not add uuids for sub-objects because then we need to define what a sub-object is.
    Also, deleting/updating (a.i. the uncommon situations) don't make sense until we can identify specific sub-objects, allowing for parallel request
    So just don't support either (a.i. to delete a representation, modify the parent image instead of using an endpoint for this purpose only)
    Adding new representations works as a separate operation"""

    representation = {
        "size": 1,
    }
    rsp = api_client.post(
        f"private/images/{existing_image['uuid']}/representations/single",
        json=representation,
    )
    assert rsp.status_code == 201, rsp.json()


def test_create_image_representation_missing_image(
    api_client: TestClient, existing_study: dict
):
    representation = {
        "accession_id": "test-representation",
        "size": 1,
    }
    rsp = api_client.post(
        f"private/images/00000000-0000-0000-0000-000000000000/representations/single",
        json=representation,
    )
    assert rsp.status_code == 404, rsp.json()


def test_get_study_images_with_filerefs(api_client: TestClient, existing_study: dict):
    """
    Get Images and filerefs mostly go through the same code path but there are differences.
    This test checks that they are filtered properly.
    Initially found as a bug
    """
    images = make_images(api_client, existing_study, 2)
    images_created = set([img["uuid"] for img in images])
    make_file_references(api_client, existing_study, 2)

    rsp = api_client.get(f"studies/{existing_study['uuid']}/images")
    assert rsp.status_code == 200
    images_fetched = set([img["uuid"] for img in rsp.json()])
    assert images_fetched == images_created


def test_get_study_images_pagination(api_client: TestClient, existing_study: dict):
    images = make_images(api_client, existing_study, 5)
    images.sort(key=lambda img: UUID(img["uuid"]).hex)
    chunk_size = 2

    # 1,2
    rsp = api_client.get(f"studies/{existing_study['uuid']}/images?limit={chunk_size}")
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    assert len(images_fetched) == chunk_size
    images_chunk = images[:2]
    assert images_chunk == images_fetched

    # 3,4
    rsp = api_client.get(
        f"studies/{existing_study['uuid']}/images?start_uuid={images_fetched[-1]['uuid']}&limit={chunk_size}"
    )
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    assert len(images_fetched) == chunk_size
    images_chunk = images[2:4]
    assert images_chunk == images_fetched

    # 5
    rsp = api_client.get(
        f"studies/{existing_study['uuid']}/images?start_uuid={images_fetched[-1]['uuid']}&limit={chunk_size}"
    )
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    assert len(images_fetched) == 1
    images_chunk = images[4:5]
    assert images_chunk == images_fetched


def test_get_study_images_pagination_large_page(
    api_client: TestClient, existing_study: dict
):
    images = make_images(api_client, existing_study, 5)
    images.sort(key=lambda img: UUID(img["uuid"]).hex)

    rsp = api_client.get(f"studies/{existing_study['uuid']}/images?limit={10000}")
    assert rsp.status_code == 200
    images_fetched = rsp.json()
    assert len(images_fetched) == 5
    assert images == images_fetched


def test_get_study_images_pagination_bad_limit(
    api_client: TestClient, existing_study: dict
):
    images = make_images(api_client, existing_study, 5)
    images.sort(key=lambda img: UUID(img["uuid"]).hex)

    rsp = api_client.get(f"studies/{existing_study['uuid']}/images?limit={0}")
    assert rsp.status_code == 422


def test_set_image_ome_metadata_update(api_client: TestClient, existing_image: dict):
    with open(os.path.join(package_base(), "tests/data/simple.ome.xml")) as f:
        rsp = api_client.post(
            f"private/images/{existing_image['uuid']}/ome_metadata",
            files={"ome_metadata_file": f.read()},
        )
        assert rsp.status_code == 201

        bia_image_ome_metadata = rsp.json()
        assert bia_image_ome_metadata["bia_image_uuid"] == existing_image["uuid"]
        assert bia_image_ome_metadata["ome_metadata"]["images"][0]["name"] == "XY-ch-02"

    rsp = api_client.get(f"images/{existing_image['uuid']}/ome_metadata")
    assert rsp.status_code == 200
    bia_image_ome_metadata = rsp.json()
    assert bia_image_ome_metadata["bia_image_uuid"] == existing_image["uuid"]
    assert bia_image_ome_metadata["ome_metadata"]["images"][0]["name"] == "XY-ch-02"


def test_set_image_ome_metadata_invalid(api_client: TestClient, existing_image: dict):
    with open(os.path.realpath(__file__)) as f:
        rsp = api_client.post(
            f"private/images/{existing_image['uuid']}/ome_metadata",
            files={"ome_metadata_file": f.read()},
        )
        assert rsp.status_code == 422

    # check no ome metadata object was created
    rsp = api_client.get(f"images/{existing_image['uuid']}/ome_metadata")
    assert rsp.status_code == 404


def test_set_image_ome_metadata_update(api_client: TestClient, existing_image: dict):
    ome_file_path = os.path.join(package_base(), "tests/data/simple.ome.xml")
    with open(ome_file_path) as f:
        rsp = api_client.post(
            f"private/images/{existing_image['uuid']}/ome_metadata",
            files={"ome_metadata_file": f.read()},
        )
        assert rsp.status_code == 201
    with open(ome_file_path) as f:
        rsp = api_client.post(
            f"private/images/{existing_image['uuid']}/ome_metadata",
            files={"ome_metadata_file": f.read()},
        )
        assert rsp.status_code == 201

    rsp = api_client.get(f"images/{existing_image['uuid']}/ome_metadata")
    assert rsp.status_code == 200


def test_search_images_exact_match_empty_query(api_client: TestClient):
    rsp = api_client.post(f"search/images/exact_match")
    assert rsp.status_code == 422


def test_search_images_exact_match_empty_result(
    api_client: TestClient, existing_study: dict
):
    rsp = api_client.post(
        f"search/images/exact_match",
        json={
            "study_uuid": existing_study["uuid"],
        },
    )
    assert rsp.status_code == 200
    assert rsp.json() == []


def test_search_images_exact_match_original_relpath(
    api_client: TestClient, existing_image: dict
):
    rsp = api_client.post(
        f"search/images/exact_match",
        json={
            "original_relpath": existing_image["original_relpath"],
        },
    )
    assert rsp.status_code == 200
    # lots of images with the same original relpath - constant in the template
    assert len(rsp.json()) != 0


def test_search_images_exact_match_all_filters(
    api_client: TestClient, existing_image: dict
):
    rsp = api_client.post(
        f"search/images/exact_match",
        json={
            "original_relpath": existing_image["original_relpath"],
            "study_uuid": existing_image["study_uuid"],
        },
    )
    assert rsp.status_code == 200
    # lots of images with the same original relpath - constant in the template
    arr_images = rsp.json()
    assert len(arr_images) == 1

    assert arr_images.pop() == existing_image


def test_search_images_exact_match_by_annotation(
    api_client: TestClient, existing_study: dict
):
    test_unique_author_email = f"test_{existing_study['uuid']}@ebi.ac.uk"

    first_img = get_template_image(existing_study=existing_study, add_uuid=True)
    first_img["annotations"] = [
        {
            "author_email": test_unique_author_email,
            "key": "first_img_annotation_key",
            "value": "first_img_annotation_value",
            "state": "active",
        }
    ]
    # adding this just to simplify equality check because annotations get applies when fetching
    first_img["attributes"]["first_img_annotation_key"] = "first_img_annotation_value"

    second_img = get_template_image(existing_study=existing_study, add_uuid=True)
    second_img["annotations"] = [
        {
            "author_email": test_unique_author_email,
            "key": "second_img_annotation_key",
            "value": "second_img_annotation_value",
            "state": "active",
        }
    ]
    # adding this just to simplify equality check because annotations get applies when fetching
    second_img["attributes"][
        "second_img_annotation_key"
    ] = "second_img_annotation_value"

    dummy_img = get_template_image(existing_study=existing_study, add_uuid=True)

    rsp = api_client.post("private/images", json=[first_img, second_img, dummy_img])
    assert rsp.status_code == 201

    params = {
        "annotations_any": [
            {
                "key": "first_img_annotation_key",
                "author_email": test_unique_author_email,
            }
        ],
    }
    rsp = api_client.post("search/images/exact_match", json=params)
    assert rsp.status_code == 200
    assert rsp.json() == [first_img]

    params["annotations_any"].append(
        {
            "key": "second_img_annotation_key",
            "author_email": test_unique_author_email,
        }
    )
    rsp = api_client.post("search/images/exact_match", json=params)
    assert rsp.status_code == 200

    # equivalent to set(rsp.json()) == {first_img, second_img} but can't make sets of dicts
    fetched_img = rsp.json()
    assert len(fetched_img) == 2
    assert first_img in fetched_img
    assert second_img in fetched_img


import copy


class TestSearchImagesExactMatch:
    @pytest.fixture
    def img_fixtures(self, api_client: TestClient, existing_study: dict) -> List[dict]:
        template_representation = {
            "size": 100,
            "uri": ["https://www.google.com/test/abc"],
            "type": "test_representation",
            "attributes": {
                "some_attr": "some_value",
            },
            "dimensions": None,
            "rendering": None,
        }

        first_img = get_template_image(existing_study=existing_study, add_uuid=True)
        first_img["representations"] = [template_representation]

        template_representation = copy.deepcopy(template_representation)
        second_img = get_template_image(existing_study=existing_study, add_uuid=True)
        template_representation |= {
            "size": 1000,
            "type": "other_test_representation",
            "attributes": {
                "some_attr": "some_value",
                "other_attr": "other_value",
            },
        }
        second_img["representations"] = [template_representation]

        # this is added to ensure filters that actually return items to which the filter doesn't apply at all don't pass
        dummy_img = get_template_image(existing_study=existing_study, add_uuid=True)

        images_created = [first_img, second_img, dummy_img]
        rsp = api_client.post("private/images", json=images_created)
        assert rsp.status_code == 201, rsp.json()

        return images_created

    def test_search_images_no_match(
        self, api_client: TestClient, img_fixtures: List[dict], existing_study: dict
    ):
        rsp = api_client.post(
            "search/images/exact_match",
            json={
                "image_representations_any": [
                    {
                        "type": "some_type_that_does_not_exist",
                    }
                ],
                "study_uuid": existing_study["uuid"],
            },
        )
        assert rsp.status_code == 200
        assert rsp.json() == []

    def test_search_size(
        self, api_client: TestClient, img_fixtures: List[dict], existing_study: dict
    ):
        rsp = api_client.post(
            "search/images/exact_match",
            json={
                "image_representations_any": [
                    {
                        "size_bounds_lte": 100,
                    }
                ],
                "study_uuid": existing_study["uuid"],
            },
        )
        assert rsp.status_code == 200
        assert unorderd_lists_equality([img_fixtures[0]], rsp.json())

        rsp = api_client.post(
            "search/images/exact_match",
            json={
                "image_representations_any": [
                    {
                        "size_bounds_lte": 100,
                        "size_bounds_gte": 100,
                    }
                ],
                "study_uuid": existing_study["uuid"],
            },
        )
        assert rsp.status_code == 200
        assert unorderd_lists_equality([img_fixtures[0]], rsp.json())

        rsp = api_client.post(
            "search/images/exact_match",
            json={
                "image_representations_any": [
                    {
                        "size_bounds_gte": 1,
                    }
                ],
                "study_uuid": existing_study["uuid"],
            },
        )
        assert rsp.status_code == 200
        assert unorderd_lists_equality(img_fixtures[:2], rsp.json())

        rsp = api_client.post(
            "search/images/exact_match",
            json={
                "image_representations_any": [
                    {
                        "size_bounds_lte": 1000,
                    }
                ],
                "study_uuid": existing_study["uuid"],
            },
        )
        assert rsp.status_code == 200
        assert unorderd_lists_equality(img_fixtures[:2], rsp.json())

    def test_search_uri_prefix(
        self, api_client: TestClient, img_fixtures: List[dict], existing_study: dict
    ):
        rsp = api_client.post(
            "search/images/exact_match",
            json={
                "image_representations_any": [
                    {
                        "uri_prefix": "https://www.google.com/test",
                    }
                ],
                "study_uuid": existing_study["uuid"],
            },
        )
        assert rsp.status_code == 200
        assert unorderd_lists_equality(img_fixtures[:2], rsp.json())

    def test_search_uri_prefix_not_substring(
        self, api_client: TestClient, img_fixtures: List[dict], existing_study: dict
    ):
        rsp = api_client.post(
            "search/images/exact_match",
            json={
                "image_representations_any": [
                    {
                        "uri_prefix": "://www.google.com/test",
                    }
                ],
                "study_uuid": existing_study["uuid"],
            },
        )
        assert rsp.status_code == 200
        assert rsp.json() == []

    def test_search_type(
        self, api_client: TestClient, img_fixtures: List[dict], existing_study: dict
    ):
        rsp = api_client.post(
            "search/images/exact_match",
            json={
                "image_representations_any": [
                    {
                        "type": "other_test_representation",
                    }
                ],
                "study_uuid": existing_study["uuid"],
            },
        )
        assert rsp.status_code == 200
        assert unorderd_lists_equality([img_fixtures[1]], rsp.json())
        assert rsp.json() == [img_fixtures[1]]

    def test_search_images_pagination(self, api_client: TestClient):
        rsp = api_client.post(
            "search/images/exact_match",
            json={
                "image_representations_any": [
                    {
                        "size_bounds_gte": 0,
                    }
                ],
                "limit": 2,
            },
        )
        assert rsp.status_code == 200

        images_fetched = rsp.json()
        assert len(images_fetched) == 2

        last_img_first_page = images_fetched[-1]["uuid"]
        rsp = api_client.post(
            "search/images/exact_match",
            json={
                "image_representations_any": [
                    {
                        "size_bounds_gte": 0,
                    }
                ],
                "limit": 2,
                "start_uuid": last_img_first_page,
            },
        )
        assert rsp.status_code == 200

        next_page_images = rsp.json()
        assert len(next_page_images) == 2

        assert last_img_first_page not in [img["uuid"] for img in next_page_images]
