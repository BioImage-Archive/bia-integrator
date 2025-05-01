from datetime import datetime
from pathlib import Path
import pytest

from bia_shared_datamodels import bia_data_model, uuid_creation
from bia_integrator_api import PrivateApi

from bia_assign_image.api_client import (
    get_local_bia_api_client,
    store_object_in_api_idempotent,
)


@pytest.fixture
def new_study_object() -> bia_data_model.Study:
    # Create unique uuid based on current timestamp
    timestamp = datetime.strftime(datetime.now(), "%d-%m-%Y-%H:%M:%S:%f")
    accession_id = f"S-BIAD-TEST-STORE-OBJECT-IN-API-IDEMPOTENT-{timestamp}"
    study_uuid = uuid_creation.create_study_uuid(accession_id)

    # Load a random study from test data
    study_path = Path(__file__).parent / "input_data" / "study"
    study_json = next(p for p in study_path.rglob("./*/*.json"))
    study = bia_data_model.Study.model_validate_json(study_json.read_text())
    study.uuid = study_uuid
    study.accession_id = accession_id
    return study


@pytest.fixture
def new_study_uuid(new_study_object) -> str:
    return str(new_study_object.uuid)


@pytest.fixture
def api_client() -> PrivateApi:
    return get_local_bia_api_client()


def compare_bia_study_object_with_api_study_object(bia_study, api_study):
    """Helper function to compare bia_data_model.Study vs api_models.Study

    This function uses the dicts of the two models and adjusts for the
    difference in type of the 'uuid' property in both. It is called by
    the tests when comparing the new_study_object with its API equivalent.
    """
    bia_study_dict = bia_study.model_dump()

    # bia_data_model.Study.uuid is UUID, but api_models.Study.uuid is str
    bia_study_dict["uuid"] = str(bia_study_dict["uuid"])

    api_study_dict = api_study.model_dump()
    return bia_study_dict == api_study_dict


def test_store_new_object(new_study_uuid, new_study_object, api_client):
    store_object_in_api_idempotent(api_client, new_study_object)
    api_copy_of_new_study = api_client.get_study(new_study_uuid)
    assert compare_bia_study_object_with_api_study_object(
        new_study_object, api_copy_of_new_study
    )


def test_store_exact_same_object_returns_object_exists_message(
    new_study_uuid, new_study_object, api_client, caplog
):
    # First save
    store_object_in_api_idempotent(api_client, new_study_object)
    api_copy_of_new_study = api_client.get_study(new_study_uuid)
    assert compare_bia_study_object_with_api_study_object(
        new_study_object, api_copy_of_new_study
    )

    # Second save of exactly the same object
    store_object_in_api_idempotent(api_client, new_study_object)

    # Check API version has not changed
    api_copy_of_new_study = api_client.get_study(new_study_uuid)
    assert compare_bia_study_object_with_api_study_object(
        new_study_object, api_copy_of_new_study
    )


def test_store_modified_object_updates_version(
    new_study_uuid, new_study_object, api_client
):
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
