from fastapi.testclient import TestClient
import pytest
from .util import (
    make_images,
    make_study,
)


def test_create_collection(api_client: TestClient, uuid: str):
    # @TODO: Does deleting a study inside a collection cascade/invalidate the collection/something else?

    study_uuids = [make_study(api_client)["uuid"] for _ in range(3)]
    collection = {
        "uuid": uuid,
        "version": 0,
        "name": "test_collection_name",
        "title": "test_collection_title",
        "subtitle": "",
        "study_uuids": study_uuids,
    }

    rsp = api_client.post(f"private/collections", json=collection)
    assert rsp.status_code == 201, rsp.json()


def test_get_image_with_uuid_of_non_image(api_client: TestClient, existing_study):
    rsp = api_client.get(f"images/{existing_study['uuid']}")
    assert rsp.status_code == 400


def test_get_object_info_by_accession(api_client: TestClient, uuid: str):
    created_study = make_study(api_client, {"accession_id": uuid})

    # rsp = api_client.get(f"object_info_by_accessions?accessions[]={uuid}")
    rsp = api_client.get(
        f"object_info_by_accessions",
        params={
            "accessions": [uuid],
        },
    )
    assert rsp.status_code == 200

    assert len(rsp.json()) == 1

    accession_info = rsp.json()[0]
    assert created_study["uuid"] == accession_info["uuid"]


def test_get_study_images_by_alias(api_client: TestClient, existing_study, uuid: str):
    make_images(
        api_client,
        existing_study,
        5,
        image_template={
            "uuid": None,
            "version": 0,
            "study_uuid": existing_study["uuid"],
            "name": f"image_name_value",
            "original_relpath": f"/home/test/image_path_value",
            "attributes": {
                "k": "v",
            },
            "annotations": [],
            "dimensions": None,
            "alias": {
                "name": f"{uuid}_test_1",
            },
            "representations": [],
        },
        expect_status=400,
    )

    rsp = api_client.get(
        f"studies/{existing_study['uuid']}/images_by_aliases",
        params={
            "aliases": [f"{uuid}_test_1"],
        },
    )
    assert rsp.status_code == 200
    # all images with the test_1 alias suffix will get rejected
    assert len(rsp.json()) == 1


def test_get_collection(api_client: TestClient, existing_collection):
    rsp = api_client.get(f"collections/{existing_collection['uuid']}")
    assert rsp.status_code == 200
    assert rsp.json() == existing_collection


def test_search_collections_no_filter(api_client: TestClient):
    rsp = api_client.get("collections")
    assert rsp.status_code == 200
    assert len(rsp.json())


def test_no_id_in_single_objects(api_client: TestClient, existing_study):
    rsp = api_client.get(f"studies/{ existing_study['uuid'] }")
    assert rsp.status_code == 200

    assert "id" not in rsp.json().keys()
    assert "_id" not in rsp.json().keys()


def test_no_id_in_list(api_client: TestClient, existing_image):
    rsp = api_client.get(f"studies/{ existing_image['study_uuid'] }/images")
    assert rsp.status_code == 200

    assert not any(["id" in img.keys() for img in rsp.json()])
    assert not any(["_id" in img.keys() for img in rsp.json()])


def test_single_doc_update_no_change_idempotent(api_client: TestClient, existing_study):
    rsp = api_client.patch("private/studies", json=existing_study)
    assert rsp.status_code == 200


def test_single_doc_update_some_change_fails(api_client: TestClient, existing_study):
    existing_study["annotations"].append(
        {
            "author_email": "test@ebi.ac.uk",
            "key": "test",
            "value": "test",
            "state": "active",
        }
    )

    rsp = api_client.patch("private/studies", json=existing_study)
    assert rsp.status_code == 404


@pytest.mark.parametrize(
    "endpoint, document_creator",
    [
        pytest.param("private/studies", "existing_study", id="create_study"),
        pytest.param(
            "private/collections", "existing_collection", id="create_collection"
        ),
        pytest.param(
            "private/biosamples", "existing_biosample", id="create_biosamples"
        ),
        pytest.param("private/specimens", "existing_specimen", id="create_specimens"),
        pytest.param(
            "private/image_acquisitions",
            "existing_image_acquisition",
            id="create_image_acquisition",
        ),
    ],
)
def test_idempotent_create(
    api_client: TestClient,
    endpoint: str,
    document_creator: str,
    request,
):
    # have to manually request fixtures values when they are different for the various parametered tests
    document = request.getfixturevalue(document_creator)
    rsp = api_client.post(endpoint, json=document, params=[("overwrite_mode", "fail")])

    rsp.status_code == 409

    rsp = api_client.post(
        endpoint, json=document, params=[("overwrite_mode", "allow_idempotent")]
    )
    assert rsp.status_code == 201


@pytest.mark.parametrize(
    "endpoint, document_creator",
    [
        pytest.param("private/images", "existing_image", id="create_images"),
        pytest.param(
            "private/file_references",
            "existing_file_reference",
            id="create_file_references",
        ),
    ],
)
def test_idempotent_create_bulk(
    api_client: TestClient,
    endpoint: str,
    document_creator: str,
    request,
):
    single_document_list = [request.getfixturevalue(document_creator)]
    rsp = api_client.post(
        endpoint, json=single_document_list, params=[("overwrite_mode", "fail")]
    )

    rsp.status_code == 400

    rsp = api_client.post(
        endpoint,
        json=single_document_list,
        params=[("overwrite_mode", "allow_idempotent")],
    )
    assert rsp.status_code == 201
