from bia_shared_datamodels import mock_objects
import uuid as uuid_lib
from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
import json
from api.settings import Settings
import asyncio

test_settings = Settings(mongo_index_push=True)

TEST_SERVER_BASE_URL = "http://localhost.com/v2"


def get_uuid() -> str:
    # @TODO: make this constant and require mongo to always be clean?
    generated = uuid_lib.uuid4()

    return str(generated)


def mock_object_jsonsafe(fn_mock_generator, passthrough={}):
    """
    makes non-json serialisable types (UUID, URL, datetime.date) into strings
    """

    obj = fn_mock_generator(**passthrough)
    str_obj = json.dumps(obj, default=lambda v: str(v))
    serialisable_obj = json.loads(str_obj) | {"version": 0, "uuid": get_uuid()}

    return serialisable_obj


@pytest.fixture(scope="function")
def uuid() -> str:
    return get_uuid()


@pytest.fixture(scope="session")
def event_loop():
    yield asyncio.get_event_loop()

    asyncio.get_event_loop().close()


def get_client():
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

    client = TestClient(
        app, base_url=TEST_SERVER_BASE_URL, raise_server_exceptions=False
    )
    return client


async def create_user_if_missing(email: str, password: str):
    """
    Exception from the general rule used in this project, of tests being as high-level as possible
    Just to avoid compromising on security for easy test user creation / the logistics of a seed db
    """
    # !! settings not used, but needs to be resolve first to avoid cyclic dependencies
    #   repro: Delete import below and run just test_minimal (not test_auth)
    from api.app import settings
    from api.models.repository import repository_create
    from api.auth import create_user, get_user

    db = await repository_create(test_settings)

    if not await get_user(db, email):
        await create_user(db, email, password)


def authenticate_client(api_client: TestClient, user_details: dict):
    rsp = api_client.post("auth/token", data=user_details)

    assert rsp.status_code == 200
    token = rsp.json()

    api_client.headers["Authorization"] = f"Bearer {token['access_token']}"


@pytest_asyncio.fixture(scope="session")
async def existing_user() -> dict:
    user_details = {
        "username": "test@example.com",
        "password": "test",
    }
    await create_user_if_missing(user_details["username"], user_details["password"])

    return user_details


@pytest.fixture(scope="module")
def settings() -> Settings:
    return test_settings


@pytest.fixture(scope="module")
def user_create_token(settings: Settings) -> str:
    return settings.user_create_secret_token


# @pytest_asyncio.fixture(scope="function")  # session
@pytest.fixture(scope="session")
def api_client(existing_user: dict):
    with get_client() as client:
        authenticate_client(client, existing_user)

        yield client


# @pytest_asyncio.fixture(scope="function")  # session
@pytest.fixture(scope="session")
def api_client_public():
    with get_client() as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def existing_study(api_client: TestClient) -> dict:
    study = mock_object_jsonsafe(
        mock_objects.get_study_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    rsp = api_client.post("private/study", json=study)
    assert rsp.status_code == 201, rsp.json()

    return study


@pytest_asyncio.fixture(scope="function")
async def updated_study(api_client: TestClient, existing_study: dict) -> dict:
    existing_study["version"] = 1

    rsp = api_client.post("private/study", json=existing_study)
    assert rsp.status_code == 201, rsp.json()

    return existing_study


@pytest_asyncio.fixture(scope="function")
async def existing_dataset(existing_study, api_client: TestClient) -> dict:
    dataset = mock_object_jsonsafe(
        mock_objects.get_dataset_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )
    dataset["submitted_in_study_uuid"] = existing_study["uuid"]

    rsp = api_client.post("private/dataset", json=dataset)
    assert rsp.status_code == 201, rsp.json()

    return dataset


@pytest_asyncio.fixture(scope="function")
async def existing_specimen_imaging_preparation_protocol(api_client: TestClient):
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


@pytest_asyncio.fixture(scope="function")
async def existing_biosample(existing_protocol, api_client: TestClient):
    biosample = mock_object_jsonsafe(
        mock_objects.get_biosample_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )
    biosample |= {"growth_protocol_uuid": existing_protocol["uuid"]}

    rsp = api_client.post(
        "private/bio_sample",
        json=biosample,
    )
    assert rsp.status_code == 201, rsp.json()

    return biosample


@pytest_asyncio.fixture(scope="function")
async def existing_protocol(
    api_client: TestClient,
):
    protocol = mock_object_jsonsafe(
        mock_objects.get_protocol_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    rsp = api_client.post(
        "private/protocol",
        json=protocol,
    )
    assert rsp.status_code == 201, rsp.json()

    return protocol


@pytest_asyncio.fixture(scope="function")
async def existing_specimen(
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


@pytest_asyncio.fixture(scope="function")
async def existing_file_reference(api_client: TestClient, existing_dataset: dict):
    file_reference = mock_object_jsonsafe(
        mock_objects.get_file_reference_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    file_reference |= {"submission_dataset_uuid": existing_dataset["uuid"]}

    rsp = api_client.post(
        "private/file_reference",
        json=file_reference,
    )
    assert rsp.status_code == 201, rsp.json()

    return file_reference


@pytest_asyncio.fixture(scope="function")
async def existing_image_acquisition_protocol(api_client: TestClient):
    image_acquisition_protocol = mock_object_jsonsafe(
        mock_objects.get_image_acquisition_protocol_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    rsp = api_client.post(
        "private/image_acquisition_protocol",
        json=image_acquisition_protocol,
    )
    assert rsp.status_code == 201, rsp.json()

    return image_acquisition_protocol


@pytest_asyncio.fixture(scope="function")
async def existing_image(
    api_client: TestClient,
    existing_creation_process: dict,
    existing_dataset: dict,
    existing_file_reference: dict,
):
    image = mock_object_jsonsafe(
        mock_objects.get_image_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )

    image |= {
        "submission_dataset_uuid": existing_dataset["uuid"],
        "creation_process_uuid": existing_creation_process["uuid"],
        "original_file_reference_uuid": [existing_file_reference["uuid"]],
    }

    rsp = api_client.post(
        "private/image",
        json=image,
    )
    assert rsp.status_code == 201, rsp.json()

    return image


@pytest_asyncio.fixture(scope="function")
async def existing_annotaton_data(
    api_client: TestClient,
    existing_image_annotation_dataset: dict,
    existing_creation_process: dict,
):
    annotation_data = mock_object_jsonsafe(
        mock_objects.get_annotation_data_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )
    annotation_data |= {
        "submission_dataset_uuid": existing_image_annotation_dataset["uuid"],
        "creation_process_uuid": existing_creation_process["uuid"],
    }

    rsp = api_client.post(
        "private/annotation_file_reference",
        json=annotation_data,
    )
    assert rsp.status_code == 201, rsp.json()

    return annotation_data


@pytest_asyncio.fixture(scope="function")
async def existing_image_representation(
    api_client: TestClient,
    existing_image: dict,
):
    image_representation = mock_object_jsonsafe(
        mock_objects.get_image_representation_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )
    image_representation |= {
        "representation_of_uuid": existing_image["uuid"],
    }

    rsp = api_client.post(
        "private/image_representation",
        json=image_representation,
    )
    assert rsp.status_code == 201, rsp.json()

    return image_representation


@pytest_asyncio.fixture(scope="function")
async def existing_creation_process(
    api_client: TestClient,
    existing_specimen: dict,
    existing_image_acquisition_protocol: dict,
):
    creation_process = mock_object_jsonsafe(
        mock_objects.get_creation_process_dict,
        passthrough={"completeness": mock_objects.Completeness.COMPLETE},
    )
    creation_process |= {
        "subject_specimen_uuid": existing_specimen["uuid"],
        "image_acquisition_protocol_uuid": [
            existing_image_acquisition_protocol["uuid"]
        ],
        "input_image_uuid": [],
        "protocol_uuid": [],
        "annotation_method_uuid": [],
    }

    rsp = api_client.post(
        "private/creation_process",
        json=creation_process,
    )
    assert rsp.status_code == 201, rsp.json()

    return creation_process
