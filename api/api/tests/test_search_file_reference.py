import pytest
from fastapi.testclient import TestClient
from api.tests.conftest import get_uuid
from typing import List


@pytest.fixture
def mock_file_references():
    return [
        {
            "object_creator": "submitter",
            "uuid": "00f8e870-255d-4102-ba8b-76f105a483c4",
            "version": 0,
            "model": {"type_name": "FileReference", "version": 3},
            "additional_metadata": [
                {"provenance": "submitter", "name": "file_list_columns", "value": {}}
            ],
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "submission_dataset_uuid": "f5eeec34-cd2c-4db8-93f0-78405dac1a09",
        },
        {
            "object_creator": "submitter",
            "uuid": "0284edc4-f2f2-4098-8e22-dd6f284e29ea",
            "version": 0,
            "model": {"type_name": "FileReference", "version": 3},
            "additional_metadata": [
                {"provenance": "submitter", "name": "file_list_columns", "value": {}}
            ],
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "submission_dataset_uuid": "7c2d6930-ecd8-45a8-b790-0ff4ecca416a",
        },
        {
            "object_creator": "submitter",
            "uuid": "0e7c5a61-a4f9-4bb3-b80b-16d6e1a9ede9",
            "version": 0,
            "model": {"type_name": "FileReference", "version": 3},
            "additional_metadata": [
                {"provenance": "submitter", "name": "file_list_columns", "value": {}}
            ],
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "submission_dataset_uuid": "507e6785-8c89-4f23-ba49-0f90da8e419f",
        },
        {
            "object_creator": "submitter",
            "uuid": "121aa82d-85e7-4dd4-80be-9524808cc1e2",
            "version": 0,
            "model": {"type_name": "FileReference", "version": 3},
            "additional_metadata": [
                {"provenance": "submitter", "name": "file_list_columns", "value": {}}
            ],
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "submission_dataset_uuid": "6271d72c-95fe-45a1-988c-c908d3f53b84",
        },
        {
            "object_creator": "submitter",
            "uuid": "14d4fbc2-6cec-471e-9d2e-20bb58cb08c6",
            "version": 0,
            "model": {"type_name": "FileReference", "version": 3},
            "additional_metadata": [
                {"provenance": "submitter", "name": "file_list_columns", "value": {}}
            ],
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "submission_dataset_uuid": "ef0a2e76-5166-4826-9fa4-dbbe05f08389",
        },
        {
            "object_creator": "submitter",
            "uuid": "2a64a7ac-3883-4aa9-a97f-b185372abdb1",
            "version": 0,
            "model": {"type_name": "FileReference", "version": 3},
            "additional_metadata": [
                {"provenance": "submitter", "name": "file_list_columns", "value": {}}
            ],
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "submission_dataset_uuid": "a5e38575-988e-49ac-a219-d746fd55cea2",
        },
        {
            "object_creator": "submitter",
            "uuid": "32809f8d-020c-4f20-bf22-528e7ecddd16",
            "version": 0,
            "model": {"type_name": "FileReference", "version": 3},
            "additional_metadata": [
                {"provenance": "submitter", "name": "file_list_columns", "value": {}}
            ],
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "submission_dataset_uuid": "e145cc3f-8ea6-450c-b3c1-d1543026470b",
        },
        {
            "object_creator": "submitter",
            "uuid": "3512c568-67d3-4c28-9fc3-b11d3b3c1356",
            "version": 0,
            "model": {"type_name": "FileReference", "version": 3},
            "additional_metadata": [
                {"provenance": "submitter", "name": "file_list_columns", "value": {}}
            ],
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "submission_dataset_uuid": "60c5d631-de65-4b4b-b547-07216b04a650",
        },
        {
            "object_creator": "submitter",
            "uuid": "36bce1ff-f0fb-4175-9c0a-02aa133fc355",
            "version": 0,
            "model": {"type_name": "FileReference", "version": 3},
            "additional_metadata": [
                {"provenance": "submitter", "name": "file_list_columns", "value": {}}
            ],
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "submission_dataset_uuid": "a95972a1-5b0a-4ac8-9c52-27e76329204b",
        },
        {
            "object_creator": "submitter",
            "uuid": "40fc6124-6754-4a97-b81d-245e362914bb",
            "version": 0,
            "model": {"type_name": "FileReference", "version": 3},
            "additional_metadata": [
                {"provenance": "submitter", "name": "file_list_columns", "value": {}}
            ],
            "file_path": "Dummy file path",
            "format": "Dummy format",
            "size_in_bytes": 10,
            "uri": "https://dummy.uri.co",
            "submission_dataset_uuid": "686304c9-1a9c-4116-9ee1-51aa5e4f2b83",
        },
    ]


def test_file_reference_page_size_enforced(
    api_client: TestClient, mock_file_references: List[dict]
):
    page_size = 2
    rsp = api_client.get(
        "/v2/search/file_reference/by_path_name",
        params={"path_name": "Dummy file path", "page_size": page_size},
    )
    assert rsp.status_code == 200
    assert len(rsp.json()) == page_size
    assert rsp.json() == mock_file_references[:2]


def test_file_reference_bad_page_size_rejected(api_client: TestClient):
    for bad in [0, -5]:
        rsp = api_client.get(
            "/v2/search/file_reference/by_path_name",
            params={"path_name": "Dummy file path", "page_size": bad},
        )
        assert rsp.status_code == 422


def test_file_reference_path_name_required(api_client: TestClient):
    rsp = api_client.get("/v2/search/file_reference/by_path_name")
    assert rsp.status_code == 422  # Missing required query param


def test_file_reference_no_results(api_client: TestClient):
    rsp = api_client.get(
        "/v2/search/file_reference/by_path_name",
        params={"path_name": "Nonexistent path", "page_size": 3},
    )
    assert rsp.status_code == 200
    assert rsp.json() == []
