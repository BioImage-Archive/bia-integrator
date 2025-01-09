from fastapi.testclient import TestClient
from api.tests.conftest import get_uuid
from api.tests.test_pagination import datasets_many
from typing import List


def test_search_existing_study(api_client: TestClient, existing_study):
    existing_study["uuid"] = get_uuid()
    existing_study["accession_id"] = existing_study["uuid"]
    rsp = api_client.post("private/study", json=existing_study)
    assert rsp.status_code == 201

    rsp = api_client.get(
        f"search/study/accession",
        params={"accession_id": existing_study["accession_id"]},
    )
    assert rsp.status_code == 200, rsp.json()
    assert rsp.json() == existing_study


def test_search_missing_study(api_client: TestClient):
    rsp = api_client.get(
        "search/study/accession",
        params={"accession_id": "this_does_not_exist"},
    )
    assert rsp.status_code == 200, rsp.json()
    assert rsp.json() == None


def test_search_image_representation(
    api_client: TestClient, existing_image_representation
):
    """
    ! Too many results if searching for the fixed image_representation
    so create a new one with a unique value and search for it
    """
    img_rep = existing_image_representation.copy()
    img_rep["uuid"] = get_uuid()

    # ! slashes (and some special characters) escaped correctly
    # (important for paths)
    search_fragment = f"{img_rep['uuid']}/*.\\*a b/c"

    img_rep["file_uri"] = [f"http://{search_fragment}/b"]
    rsp = api_client.post("private/image_representation", json=img_rep)
    assert rsp.status_code == 201

    rsp = api_client.get(
        "search/image_representation/file_uri_fragment",
        params={"file_uri": search_fragment, "page_size": 100},
    )
    assert rsp.status_code == 200
    assert rsp.json() == [img_rep]


def test_search_image_representation_empty(api_client: TestClient):
    """
    ! regex-based search, so empty queries match all
    """

    rsp = api_client.get(
        "search/image_representation/file_uri_fragment",
        params={"file_uri": ""},
    )
    assert rsp.status_code == 422


def test_search_image_multiple_results(
    api_client: TestClient, existing_image_representation
):
    rsp = api_client.get(
        "search/image_representation/file_uri_fragment",
        params={
            "file_uri": existing_image_representation["file_uri"][0],
            "page_size": 100,
        },
    )
    assert rsp.status_code == 200
    assert len(rsp.json()) > 1


def test_get_multi(api_client: TestClient, datasets_many: List[dict]):
    rsp = api_client.get(
        f"search/dataset",
        params={
            "filter_uuid": [datasets_many[0]["uuid"], datasets_many[1]["uuid"]],
            "page_size": 100,
        },
    )
    assert rsp.status_code == 200
    assert len(rsp.json()) == 2
    assert rsp.json() == datasets_many[:2]


def test_get_multi_empty_filter(api_client: TestClient, datasets_many: List[dict]):
    rsp = api_client.get(
        f"search/dataset",
        params={"page_size": 3},
    )
    assert rsp.status_code == 200
    assert len(rsp.json()) == 3


def test_get_multi_mistyped_filter_ignored(
    api_client: TestClient, existing_study: dict, datasets_many: List[dict]
):
    """
    uuid is a filter to the result set,
    so if the result set didn't contain a uuid that was passed (e.g. study uuid as a dataset) it's just not used
    """
    rsp = api_client.get(
        f"search/dataset",
        params={
            "filter_uuid": [datasets_many[0]["uuid"], existing_study["uuid"]],
            "page_size": 100,
        },
    )
    assert rsp.status_code == 200
    assert len(rsp.json()) == 1
    assert rsp.json() == [datasets_many[0]]
