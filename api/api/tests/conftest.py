from bia_shared_datamodels import mock_objects, bia_data_model
import uuid as uuid_lib
from fastapi.testclient import TestClient
import pytest
import json
import jsonpickle

TEST_SERVER_BASE_URL = "http://localhost.com/v2"


def mock_object_jsonsafe(fn_mock_generator, passthrough={}):
    """
    makes non-json serialisable types (UUID, URL, datetime.date) into strings
    """

    obj = fn_mock_generator(**passthrough)
    str_obj = json.dumps(obj, default=lambda v: str(v))
    serialisable_obj = json.loads(str_obj)

    return serialisable_obj


def get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid_lib.uuid4()

    return str(generated)


def get_client(**kwargs) -> TestClient:
    from fastapi.responses import JSONResponse
    from fastapi import Request
    import traceback

    from ..app import app

    @app.exception_handler(Exception)
    def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=traceback.format_exception(exc, value=exc, tb=exc.__traceback__),
        )

    return TestClient(app, base_url=TEST_SERVER_BASE_URL, **kwargs)


@pytest.fixture(scope="module")
def api_client() -> TestClient:
    client = get_client(raise_server_exceptions=False)
    # authenticate_client(client)  # @TODO: DELETEME

    return client


@pytest.fixture(scope="function")
def existing_study(api_client: TestClient) -> dict:
    study = mock_object_jsonsafe(
        mock_objects.get_study_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    rsp = api_client.post("private/study", json=study)
    assert rsp.status_code == 201, rsp.json()

    return study


@pytest.fixture(scope="function")
def existing_experimental_imaging_dataset(
    existing_study, api_client: TestClient
) -> dict:
    dataset = mock_object_jsonsafe(
        mock_objects.get_experimental_imaging_dataset_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )
    dataset["submitted_in_study_uuid"] = existing_study["uuid"]

    rsp = api_client.post("private/experimental_imaging_dataset", json=dataset)
    assert rsp.status_code == 201, rsp.json()

    return dataset


@pytest.fixture(scope="function")
def existing_specimen_imaging_preparation_protocol(api_client: TestClient):
    specimen_imaging_preparation_protocol = mock_object_jsonsafe(
        mock_objects.get_specimen_imaging_preparation_protocol_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    rsp = api_client.post(
        "private/specimen_imaging_preparation_protocol",
        json=specimen_imaging_preparation_protocol,
    )
    assert rsp.status_code == 201, rsp.json()

    return specimen_imaging_preparation_protocol


@pytest.fixture(scope="function")
def existing_biosample(api_client: TestClient):
    biosample = mock_object_jsonsafe(
        mock_objects.get_biosample_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    rsp = api_client.post(
        "private/bio_sample",
        json=biosample,
    )
    assert rsp.status_code == 201, rsp.json()

    return biosample


@pytest.fixture(scope="function")
def existing_specimen(
    api_client: TestClient,
    existing_specimen_imaging_preparation_protocol,
    existing_biosample,
):
    specimen = mock_object_jsonsafe(
        mock_objects.get_specimen_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )
    specimen |= {
        "imaging_preparation_protocol_uuid": [
            existing_specimen_imaging_preparation_protocol["uuid"]
        ],
        "sample_of_uuid": [existing_biosample["uuid"]],
    }

    rsp = api_client.post(
        "private/specimen",
        json=specimen,
    )
    assert rsp.status_code == 201, rsp.json()

    return specimen
