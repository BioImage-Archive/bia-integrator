import pytest
from fastapi.testclient import TestClient
from api.tests.conftest import get_uuid
from typing import List


@pytest.fixture(scope="function")
def file_references_many(
    api_client: TestClient, existing_file_reference: dict, existing_dataset: dict
):
    """
    Creates several FileReference objects that share the same file_path.
    """
    file_references = [existing_file_reference]
    study_id = existing_dataset["submitted_in_study_uuid"]
    for _ in range(5):
        new_ref = existing_file_reference.copy()
        new_ref["file_path"] = "test file path"
        new_ref["uuid"] = get_uuid()
        new_ref["submission_dataset_uuid"] = existing_dataset["uuid"]
        rsp = api_client.post("private/file_reference", json=new_ref)
        assert rsp.status_code == 201, rsp.json()
        file_references.append(new_ref)

    file_references.sort(key=lambda fr: fr["uuid"])
    return {"file_references": file_references, "study_id": study_id}


def test_file_reference_path_name(api_client: TestClient, file_references_many: dict):
    page_size = 3
    file_path = "test file path"
    rsp = api_client.get(
        "/v2/search/file_reference/by_path_name",
        params={"path_name": file_path, "page_size": page_size},
    )
    file_references = [
        fr
        for fr in file_references_many["file_references"]
        if fr["file_path"] == file_path
    ][:page_size]

    assert rsp.status_code == 200
    assert len(rsp.json()) == page_size
    actual_sorted = sorted(rsp.json(), key=lambda fr: fr["uuid"])
    expected_sorted = sorted(file_references, key=lambda fr: fr["uuid"])
    assert actual_sorted == expected_sorted


def test_file_reference_path_name_with_study(
    api_client: TestClient, file_references_many: dict
):
    page_size = 5
    study_id = file_references_many["study_id"]
    file_path = "test file path"
    rsp = api_client.get(
        "/v2/search/file_reference/by_path_name",
        params={
            "path_name": file_path,
            "page_size": page_size,
            "uuid": study_id,
        },
    )
    file_references = [
        fr
        for fr in file_references_many["file_references"]
        if fr["file_path"] == file_path
    ][:page_size]

    assert rsp.status_code == 200
    assert len(rsp.json()) == page_size
    actual_sorted = sorted(rsp.json(), key=lambda fr: fr["uuid"])
    expected_sorted = sorted(file_references, key=lambda fr: fr["uuid"])
    assert actual_sorted == expected_sorted


def test_file_reference_bad_page_size_rejected(api_client: TestClient):
    for bad in [0, -5]:
        rsp = api_client.get(
            "/v2/search/file_reference/by_path_name",
            params={"path_name": "Dummy file path", "page_size": bad},
        )
        assert rsp.status_code == 422


def test_file_reference_path_name_required(api_client: TestClient):
    rsp = api_client.get("/v2/search/file_reference/by_path_name")
    assert rsp.status_code == 422
