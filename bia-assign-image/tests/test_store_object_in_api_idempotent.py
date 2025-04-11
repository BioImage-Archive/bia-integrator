import logging
from datetime import datetime
from pathlib import Path
import pytest

from bia_shared_datamodels import bia_data_model, uuid_creation
from bia_integrator_api import PrivateApi
from bia_integrator_api.exceptions import NotFoundException

from bia_assign_image.api_client import (
    get_local_bia_api_client,
    store_object_in_api_idempotent,
)


@pytest.fixture
def new_study_object() -> bia_data_model.Study:
    # Create unique uuid based on current timestamp
    timestamp = datetime.strftime(datetime.now(), "%d-%m-%Y-%H:%M:%S:%f")
    study_uuid = uuid_creation.create_study_uuid(timestamp)

    # Load study from test data
    study_path = Path(__file__).parent / "input_data" / "study"
    study_json = next(p for p in study_path.rglob("./*/*.json"))
    study = bia_data_model.Study.model_validate_json(study_json.read_text())
    study.uuid = study_uuid
    return study


@pytest.fixture
def new_study_uuid(new_study_object) -> str:
    return str(new_study_object.uuid)


@pytest.fixture
def api_client() -> PrivateApi:
    return get_local_bia_api_client()


def compare_bia_study_object_with_api_study_object(bia_study, api_study):
    bia_study_dict = bia_study.model_dump()

    # bia_data_model.Study.uuid is UUID, but api_models.Study.uuid is str
    bia_study_dict["uuid"] = str(bia_study_dict["uuid"])

    api_study_dict = api_study.model_dump()
    return bia_study_dict == api_study_dict


def test_store_new_object(new_study_uuid, new_study_object, api_client):
    # Ensure the object is not in the API
    with pytest.raises(NotFoundException):
        api_copy_of_new_study = api_client.get_study(new_study_uuid)

    store_object_in_api_idempotent(api_client, new_study_object)
    api_copy_of_new_study = api_client.get_study(new_study_uuid)
    assert compare_bia_study_object_with_api_study_object(
        new_study_object, api_copy_of_new_study
    )


def test_store_exact_same_object_returns_object_exists_message(
    new_study_uuid, new_study_object, api_client, caplog
):
    # Ensure the object is not in the API
    with pytest.raises(NotFoundException):
        api_copy_of_new_study = api_client.get_study(new_study_uuid)

    # First save
    store_object_in_api_idempotent(api_client, new_study_object)
    api_copy_of_new_study = api_client.get_study(new_study_uuid)
    assert compare_bia_study_object_with_api_study_object(
        new_study_object, api_copy_of_new_study
    )

    # Second save
    with caplog.at_level(logging.INFO):
        store_object_in_api_idempotent(api_client, new_study_object)
    expected_info_text = f"Not persisting current object as identical object Study with UUID {new_study_uuid} already exists in API."
    assert expected_info_text in caplog.text

    api_copy_of_new_study = api_client.get_study(new_study_uuid)
    assert compare_bia_study_object_with_api_study_object(
        new_study_object, api_copy_of_new_study
    )


def test_store_modified_object_updates_version(
    new_study_uuid, new_study_object, api_client
):
    # Ensure the object is not in the API
    with pytest.raises(NotFoundException):
        api_copy_of_new_study = api_client.get_study(new_study_uuid)

    # First save
    store_object_in_api_idempotent(api_client, new_study_object)
    api_copy_of_new_study = api_client.get_study(new_study_uuid)
    assert compare_bia_study_object_with_api_study_object(
        new_study_object, api_copy_of_new_study
    )

    # Save modified version
    new_study_object.title += "Modified"
    store_object_in_api_idempotent(api_client, new_study_object)
    api_copy_of_new_study = api_client.get_study(new_study_uuid)

    assert api_copy_of_new_study.version == new_study_object.version + 1

    # Update new_study_object version before comparing
    new_study_object.version += 1
    assert compare_bia_study_object_with_api_study_object(
        new_study_object, api_copy_of_new_study
    )
