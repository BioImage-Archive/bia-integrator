from bia_shared_datamodels import mock_objects
import uuid as uuid_lib
from fastapi.testclient import TestClient
import pytest
import json
from api.settings import Settings

import asyncio

test_settings = Settings(mongo_index_push=True)

TEST_SERVER_BASE_URL = "http://localhost.com/v2"


def mock_object_jsonsafe(fn_mock_generator, passthrough={}):
    """
    makes non-json serialisable types (UUID, URL, datetime.date) into strings
    """

    obj = fn_mock_generator(**passthrough)
    str_obj = json.dumps(obj, default=lambda v: str(v))
    serialisable_obj = json.loads(str_obj) | {"version": 0}

    return serialisable_obj


def get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid_lib.uuid4()

    return str(generated)


@pytest.fixture(scope="function")
def uuid() -> str:
    return get_uuid()


def get_client(**kwargs) -> TestClient:
    from fastapi.responses import JSONResponse
    from fastapi import Request
    import traceback

    from api.app import app

    @app.exception_handler(Exception)
    def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content=traceback.format_exception(exc, value=exc, tb=exc.__traceback__),
        )

    return TestClient(app, base_url=TEST_SERVER_BASE_URL, **kwargs)


def create_user_if_missing(email: str, password: str):
    """
    Exception from the general rule used in this project, of tests being as high-level as possible
    Just to avoid compromising on security for easy test user creation / the logistics of a seed db
    """
    # !! settings not used, but needs to be resolve first to avoid cyclic dependencies
    #   repro: Delete import below and run just test_minimal (not test_auth)
    from api.app import settings
    from api.models.repository import repository_create
    from api.auth import create_user, get_user

    loop = asyncio.get_event_loop()

    async def create_test_user_if_missing():
        db = await repository_create(test_settings)

        if not await get_user(db, email):
            await create_user(db, email, password)

    loop.run_until_complete(create_test_user_if_missing())


def authenticate_client(api_client: TestClient, user_details: dict):
    rsp = api_client.post("auth/token", data=user_details)

    assert rsp.status_code == 200
    token = rsp.json()

    api_client.headers["Authorization"] = f"Bearer {token['access_token']}"


@pytest.fixture(scope="module")
def existing_user() -> dict:
    user_details = {
        "username": "test@example.com",
        "password": "test",
    }
    create_user_if_missing(user_details["username"], user_details["password"])

    return user_details


@pytest.fixture(scope="module")
def settings() -> Settings:
    return test_settings


@pytest.fixture(scope="module")
def user_create_token(settings: Settings) -> str:
    return settings.user_create_secret_token


@pytest.fixture(scope="module")
def api_client(existing_user: dict) -> TestClient:
    client = get_client(raise_server_exceptions=False)
    authenticate_client(client, existing_user)  # @TODO: DELETEME

    return client


@pytest.fixture(scope="module")
def api_client_public() -> TestClient:
    client = get_client(raise_server_exceptions=False)

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
def updated_study(api_client: TestClient, existing_study: dict) -> dict:
    existing_study["version"] = 1

    rsp = api_client.post("private/study", json=existing_study)
    assert rsp.status_code == 201, rsp.json()

    return existing_study


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
def existing_specimen_growth_protocol(
    api_client: TestClient,
):
    specimen_growth_protocol = mock_object_jsonsafe(
        mock_objects.get_specimen_growth_protocol_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    rsp = api_client.post(
        "private/specimen_growth_protocol",
        json=specimen_growth_protocol,
    )
    assert rsp.status_code == 201, rsp.json()

    return specimen_growth_protocol


@pytest.fixture(scope="function")
def existing_specimen(
    api_client: TestClient,
    existing_specimen_imaging_preparation_protocol,
    existing_biosample,
    existing_specimen_growth_protocol,
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
        "growth_protocol_uuid": [existing_specimen_growth_protocol["uuid"]],
    }

    rsp = api_client.post(
        "private/specimen",
        json=specimen,
    )
    assert rsp.status_code == 201, rsp.json()

    return specimen


@pytest.fixture(scope="function")
def existing_file_reference(
    api_client: TestClient, existing_experimental_imaging_dataset: dict
):
    file_reference = mock_object_jsonsafe(
        mock_objects.get_file_reference_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    file_reference |= {
        "submission_dataset_uuid": existing_experimental_imaging_dataset["uuid"]
    }

    rsp = api_client.post(
        "private/file_reference",
        json=file_reference,
    )
    assert rsp.status_code == 201, rsp.json()

    return file_reference


@pytest.fixture(scope="function")
def existing_image_acquisition(api_client: TestClient):
    image_acquisition = mock_object_jsonsafe(
        mock_objects.get_image_acquisition_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    rsp = api_client.post(
        "private/image_acquisition",
        json=image_acquisition,
    )
    assert rsp.status_code == 201, rsp.json()

    return image_acquisition


@pytest.fixture(scope="function")
def existing_experimentally_captured_image(
    api_client: TestClient,
    existing_specimen: dict,
    existing_experimental_imaging_dataset: dict,
    existing_image_acquisition: dict,
):
    experimentally_captured_image = mock_object_jsonsafe(
        mock_objects.get_experimentally_captured_image_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    experimentally_captured_image |= {
        "subject_uuid": existing_specimen["uuid"],
        "submission_dataset_uuid": existing_experimental_imaging_dataset["uuid"],
        "acquisition_process_uuid": [existing_image_acquisition["uuid"]],
    }

    rsp = api_client.post(
        "private/experimentally_captured_image",
        json=experimentally_captured_image,
    )
    assert rsp.status_code == 201, rsp.json()

    return experimentally_captured_image


@pytest.fixture(scope="function")
def existing_image_annotation_dataset(api_client: TestClient, existing_study: dict):
    image_annotation_dataset = mock_object_jsonsafe(
        mock_objects.get_image_annotation_dataset_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )
    image_annotation_dataset |= {"submitted_in_study_uuid": existing_study["uuid"]}

    rsp = api_client.post(
        "private/image_annotation_dataset",
        json=image_annotation_dataset,
    )
    assert rsp.status_code == 201, rsp.json()

    return image_annotation_dataset


@pytest.fixture(scope="function")
def existing_annotaton_file_reference(
    api_client: TestClient, existing_image_annotation_dataset: dict
):
    annotation_file_reference = mock_object_jsonsafe(
        mock_objects.get_annotation_file_reference_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )
    annotation_file_reference |= {
        "submission_dataset_uuid": existing_image_annotation_dataset["uuid"],
        "source_image_uuid": [],
        "creation_process_uuid": [],
    }

    rsp = api_client.post(
        "private/annotation_file_reference",
        json=annotation_file_reference,
    )
    assert rsp.status_code == 201, rsp.json()

    return annotation_file_reference


@pytest.fixture(scope="function")
def existing_derived_image(
    api_client: TestClient, existing_image_annotation_dataset: dict
):
    derived_image = mock_object_jsonsafe(
        mock_objects.get_derived_image_dict,
        passthrough={"completeness": mock_objects.Completeness.MINIMAL},
    )
    derived_image |= {
        "submission_dataset_uuid": existing_image_annotation_dataset["uuid"]
    }

    rsp = api_client.post(
        "private/derived_image",
        json=derived_image,
    )
    assert rsp.status_code == 201, rsp.json()

    return derived_image


@pytest.fixture(scope="function")
def existing_image_representation(
    api_client: TestClient,
    existing_experimentally_captured_image: dict,
    existing_file_reference: dict,
):
    image_representation = mock_object_jsonsafe(
        mock_objects.get_image_representation_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )
    image_representation |= {
        "representation_of_uuid": existing_experimentally_captured_image["uuid"],
        "original_file_reference_uuid": [existing_file_reference["uuid"]],
    }

    rsp = api_client.post(
        "private/image_representation",
        json=image_representation,
    )
    assert rsp.status_code == 201, rsp.json()

    return image_representation
