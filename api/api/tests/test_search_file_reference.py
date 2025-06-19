import pytest
from fastapi.testclient import TestClient
from api.tests.conftest import get_uuid
from typing import List


@pytest.fixture(scope="function")
def file_references_many(
    api_client: TestClient, existing_file_reference: dict, existing_dataset: dict
):
    """
    Creates two datasets part of the same study with same file_path in the FileReference
    along with several FileReference objects that share the same file_path within the dataset.
    """
    file_references = [existing_file_reference]

    def create_new_file_references(
        file_references, existing_file_reference, dataset_uuid, number_of_fr
    ):
        for _ in range(number_of_fr):
            new_ref = existing_file_reference.copy()
            new_ref["file_path"] = "test file path"
            new_ref["uuid"] = get_uuid()
            new_ref["submission_dataset_uuid"] = dataset_uuid
            rsp = api_client.post("private/file_reference", json=new_ref)
            assert rsp.status_code == 201, rsp.json()
            file_references.append(new_ref)
        return file_references

    new_dataset = existing_dataset.copy()
    new_dataset["uuid"] = get_uuid()
    rsp = api_client.post("private/dataset", json=new_dataset)
    assert rsp.status_code == 201, rsp.json()

    file_references = create_new_file_references(
        file_references, existing_file_reference, new_dataset["uuid"], 2
    )
    file_references = create_new_file_references(
        file_references, existing_file_reference, existing_dataset["uuid"], 3
    )

    file_references.sort(key=lambda fr: fr["uuid"])
    return file_references


def test_file_reference_search_by_path_name_and_study_uuid(
    api_client: TestClient, file_references_many: List[dict], existing_dataset: dict
):
    study_id = existing_dataset["submitted_in_study_uuid"]
    file_path = "test file path"
    rsp = api_client.get(
        "/v2/search/file_reference/by_path_name",
        params={
            "path_name": file_path,
            "study_uuid": study_id,
        },
    )
    file_references = [
        fr for fr in file_references_many if fr["file_path"] == file_path
    ]

    assert rsp.status_code == 200
    actual_sorted = sorted(rsp.json(), key=lambda fr: fr["uuid"])
    expected_sorted = sorted(file_references, key=lambda fr: fr["uuid"])
    assert actual_sorted == expected_sorted


def test_file_reference_search_study_uuid_required(
    api_client: TestClient, existing_dataset: dict
):
    rsp = api_client.get(
        "/v2/search/file_reference/by_path_name",
        params={
            "study_uuid": existing_dataset["submitted_in_study_uuid"],
        },
    )
    assert rsp.status_code == 422


def test_file_reference_search_path_name_required(
    api_client: TestClient, existing_file_reference: dict
):
    rsp = api_client.get(
        "/v2/search/file_reference/by_path_name",
        params={"path_name": existing_file_reference["file_path"]},
    )
    assert rsp.status_code == 422
