# conftest files are read by pytest and fixtures get imported at the directory level and deeper.
# features in conftests files in deeper folders can overwrite features in higher level directories.
# see more here: https://docs.pytest.org/en/6.2.x/fixture.html#conftest-py-sharing-fixtures-across-multiple-files

from fastapi.testclient import TestClient

import pytest
from .util import (
    get_client,
    authenticate_client,
    get_uuid,
    make_biosample,
    make_collection,
    make_image_acquisition,
    make_specimen,
    make_study,
    get_template_file_reference,
    get_template_image,
)


@pytest.fixture(scope="module")
def api_client_public() -> TestClient:
    client = get_client(raise_server_exceptions=False)

    return client


@pytest.fixture(scope="module")
def api_client() -> TestClient:
    client = get_client(raise_server_exceptions=False)
    authenticate_client(client)  # @TODO: DELETEME

    return client


@pytest.fixture(scope="function")
def uuid() -> str:
    return get_uuid()


@pytest.fixture(scope="function")
def existing_study(api_client: TestClient):
    return make_study(api_client)


@pytest.fixture(scope="function")
def existing_biosample(api_client: TestClient):
    return make_biosample(api_client)


@pytest.fixture(scope="function")
def existing_specimen(api_client: TestClient, existing_biosample: dict):
    return make_specimen(api_client, existing_biosample)


@pytest.fixture(scope="function")
def existing_image_acquisition(api_client: TestClient, existing_specimen: dict):
    return make_image_acquisition(api_client, existing_specimen)


@pytest.fixture(scope="function")
def existing_collection(api_client: TestClient):
    return make_collection(api_client)


@pytest.fixture(scope="function")
def existing_file_reference(api_client: TestClient, existing_study: dict):
    file_reference = get_template_file_reference(existing_study, add_uuid=True)

    rsp = api_client.post("private/file_references", json=[file_reference])
    assert rsp.status_code == 201, rsp.json()

    rsp_get_fileref = api_client.get(f"file_references/{file_reference['uuid']}")
    assert rsp_get_fileref.status_code == 200

    return rsp_get_fileref.json()


@pytest.fixture(scope="function")
def existing_image(api_client: TestClient, existing_study: dict):
    image = get_template_image(existing_study, add_uuid=True)

    rsp = api_client.post("private/images", json=[image])
    assert rsp.status_code == 201, rsp.json()

    rsp_get_image = api_client.get(f"images/{image['uuid']}")
    assert rsp_get_image.status_code == 200

    return rsp_get_image.json()
