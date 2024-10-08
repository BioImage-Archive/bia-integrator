import pytest
from fastapi.testclient import TestClient
from api.tests.conftest import get_uuid
from typing import List


# @TODO: Speedup by making this scope=module,
#   but needs manually wired function-scoped dependencies
@pytest.fixture(scope="function")
def datasets_many(
    api_client: TestClient,
    existing_experimental_imaging_dataset: dict,
):
    datasets = [existing_experimental_imaging_dataset]
    for _ in range(4):
        new_dataset = existing_experimental_imaging_dataset.copy() | {
            "uuid": get_uuid()
        }
        rsp = api_client.post("private/experimental_imaging_dataset", json=new_dataset)
        assert rsp.status_code == 201, rsp.json()

        datasets.append(new_dataset)

    # same order as paginated results to make asserts easy
    datasets.sort(key=lambda d: d["uuid"])

    return datasets


def test_page_size_enforced(
    api_client: TestClient, existing_study: dict, datasets_many: List[dict]
):
    page_size = 2

    rsp = api_client.get(
        f"study/{existing_study['uuid']}/experimental_imaging_dataset?page_size={page_size}"
    )
    assert rsp.status_code == 200
    assert len(rsp.json()) == page_size
    assert rsp.json() == datasets_many[:2]


def test_large_page_exhausts_results(
    api_client: TestClient, existing_study: dict, datasets_many: List[dict]
):
    rsp = api_client.get(
        f"study/{existing_study['uuid']}/experimental_imaging_dataset?page_size=1000"
    )
    assert rsp.status_code == 200
    assert len(rsp.json()) == len(datasets_many)
    assert rsp.json() == datasets_many


def test_bad_page_size_rejected(
    api_client: TestClient, existing_study: dict, datasets_many: List[dict]
):
    rsp = api_client.get(
        f"study/{existing_study['uuid']}/experimental_imaging_dataset",
        params={"page_size": -1},
    )
    assert rsp.status_code == 422

    rsp = api_client.get(
        f"study/{existing_study['uuid']}/experimental_imaging_dataset",
        params={"page_size": 0},
    )
    assert rsp.status_code == 422


def test_page_excludes_start_uuid(
    api_client: TestClient, existing_study: dict, datasets_many: List[dict]
):
    rsp = api_client.get(
        f"study/{existing_study['uuid']}/experimental_imaging_dataset",
        params={"page_size": 2, "start_uuid": datasets_many[0]["uuid"]},
    )
    assert rsp.status_code == 200
    assert rsp.json() == datasets_many[1:3]


def test_start_uuid_untyped(
    api_client: TestClient, existing_study: dict, datasets_many: List[dict]
):
    """
    This just fixes behaviour - start_uuid in pagination isn't validated to be of the same type as the objects being paginated
    """
    rsp = api_client.get(
        f"study/{existing_study['uuid']}/experimental_imaging_dataset",
        params={"page_size": 100, "start_uuid": existing_study["uuid"]},
    )
    assert rsp.status_code == 200


def test_paginate_full_result_list(
    api_client: TestClient, existing_study: dict, datasets_many: List[dict]
):
    rsp = api_client.get(
        f"study/{existing_study['uuid']}/experimental_imaging_dataset",
        params={"page_size": 3},
    )
    assert rsp.status_code == 200
    first_page = rsp.json()

    rsp = api_client.get(
        f"study/{existing_study['uuid']}/experimental_imaging_dataset",
        params={"page_size": 3, "start_uuid": first_page[-1]["uuid"]},
    )
    assert rsp.status_code == 200
    second_page = rsp.json()

    assert first_page + second_page == datasets_many
