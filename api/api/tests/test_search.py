from fastapi.testclient import TestClient
from api.tests.conftest import get_uuid


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
    assert rsp.status_code == 404, rsp.json()


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
        params={"file_uri": search_fragment},
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
        params={"file_uri": existing_image_representation["file_uri"][0]},
    )
    assert rsp.status_code == 200
    assert len(rsp.json()) > 1
