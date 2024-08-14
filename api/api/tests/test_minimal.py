"""
WIP minimal tests
tl;dr avoid importing get_uuid to make sure we reuse mocks
"""

from fastapi.testclient import TestClient
from .conftest import get_uuid


def test_get_created_study(api_client: TestClient, existing_study):
    rsp = api_client.get(f"study/{existing_study['uuid']}")
    assert rsp.status_code == 200, rsp.text
    assert rsp.json() == existing_study


def test_get_study_datasets(
    api_client: TestClient, existing_study, existing_experimental_imaging_dataset
):
    rsp = api_client.get(f"study/{existing_study['uuid']}/experimental_imaging_dataset")
    assert rsp.status_code == 200, rsp.json()
    assert rsp.json() == [existing_experimental_imaging_dataset]


def test_get_biosample_specimens(
    api_client: TestClient, existing_biosample, existing_specimen
):
    rsp = api_client.get(f"bio_sample/{existing_biosample['uuid']}/specimen")
    assert rsp.status_code == 200, rsp.json()
    assert rsp.json() == [existing_specimen]


def test_create_object_missing_dependency_fails(
    api_client: TestClient, existing_specimen: dict
):
    """
    overwrite uuid and sample uuid on an existing specimen to get a new specimen with a missing sample uuid
    """
    specimen = existing_specimen.copy()
    specimen["uuid"] = get_uuid()
    specimen["sample_of_uuid"] = [get_uuid()]

    rsp = api_client.post(
        "private/specimen",
        json=specimen,
    )
    assert rsp.status_code == 404, rsp.json()

    # Error should mention the uuid referenced in sample_of_uuid that doesn't exist
    rsp_body = rsp.json()
    assert specimen["sample_of_uuid"][0] in rsp_body["detail"]


def test_create_object_mistyped_dependency_fails(
    api_client: TestClient, existing_specimen: dict, existing_study: dict
):
    specimen = existing_specimen.copy()
    specimen["uuid"] = get_uuid()
    specimen["imaging_preparation_protocol_uuid"] = [existing_study["uuid"]]

    rsp = api_client.post(
        "private/specimen",
        json=specimen,
    )
    assert rsp.status_code == 404, rsp.json()

    # Error message should mention the referenced uuid that doesn't exist
    rsp_body = rsp.json()
    assert specimen["imaging_preparation_protocol_uuid"][0] in rsp_body["detail"]


def test_create_object_duplicate_dependency_fails(
    api_client: TestClient, existing_specimen: dict
):
    """
    accidental feature of the dependency check implementation
       if a list of referenced objects contains duplicates (presumably there by accident), object creation should fail
    except the error is "Not found" instead of something to do with duplicates
    """

    specimen = existing_specimen.copy()
    specimen["uuid"] = get_uuid()
    specimen["sample_of_uuid"] = specimen["sample_of_uuid"] + specimen["sample_of_uuid"]

    rsp = api_client.post(
        "private/specimen",
        json=specimen,
    )
    assert rsp.status_code == 404, rsp.json()

    # Error message should mention the referenced uuid that doesn't exist
    rsp_body = rsp.json()
    assert specimen["sample_of_uuid"][0] in rsp_body["detail"]


def test_duplicate_uuid_fails(
    api_client: TestClient, existing_specimen: dict, existing_study: dict
):
    """
    ! Should fail (maybe with a different status code)
    Needs indices
    """
    specimen = existing_specimen.copy()
    specimen["uuid"] = existing_study["uuid"]

    rsp = api_client.post(
        "private/specimen",
        json=specimen,
    )
    assert rsp.status_code == 404, rsp.json()


def test_object_update_version_bumped_passes():
    assert 0, "TODO: indices then add this"
