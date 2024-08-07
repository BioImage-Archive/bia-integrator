"""
WIP minimal tests
tl;dr avoid importing get_uuid to make sure we reuse mocks
"""

from fastapi.testclient import TestClient


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
