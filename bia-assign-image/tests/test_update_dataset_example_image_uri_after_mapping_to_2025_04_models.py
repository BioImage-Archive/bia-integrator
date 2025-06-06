import os
from pathlib import Path
import json
import pytest
from bia_integrator_api.exceptions import NotFoundException
from bia_assign_image.api_client import (
    get_local_bia_api_client,
    store_object_in_api_idempotent,
)
from .conftest import get_expected_object

# Modify python path to allow importing script functions
mapping_script_path = str(Path(__file__).parents[1] / "scripts")
python_path = os.environ.get("PYTHONPATH", "")
os.environ["PYTHONPATH"] = ";".join(
    [
        mapping_script_path,
        python_path,
    ]
)
from scripts.map_image_related_artefacts_to_2025_04_models import (
    update_dataset_example_image_uri,
)

accession_id = "S-BIAD-MAP-IMAGE-RELATED-ARTEFACTS-TO-2025-04-MODELS-TEST"


@pytest.fixture
def base_path() -> Path:
    return Path(__file__).parent / "test_data" / "migrate_to_2025_04_models"


@pytest.fixture
def old_bia_study_metadata(base_path) -> dict:
    old_bia_study_metadata_path = (
        base_path / "test_update_example_image_uri" / "bia-study-metadata.json"
    )
    old_bia_study_metadata = json.loads(old_bia_study_metadata_path.read_text())
    return old_bia_study_metadata


@pytest.fixture
def image_uuid() -> str:
    return "321af7aa-4299-4ad2-9ab6-f1ac50b28174"


@pytest.fixture
def expected_updated_dataset_uuid() -> str:
    return "4e59fb10-5b86-4caf-bbca-02360078c6cb"


@pytest.fixture
def reset_expected_updated_dataset(
    base_path, expected_updated_dataset_uuid, image_uuid
):
    """Ensure this dataset is present with no example image uri

    Inclusion in API is done here as opposed to with input_data/data_in_api
    because we want to ensure the example_image_uri is always empty before the
    test. Modifying it causes issues with data_in_api.py during multiple runs.
    """
    api_client = get_local_bia_api_client()
    obj_base_path = base_path / "test_update_example_image_uri"
    try:
        dataset = api_client.get_dataset(expected_updated_dataset_uuid)
        dataset.example_image_uri = []
        store_object_in_api_idempotent(api_client, dataset)
    except NotFoundException:
        dataset = get_expected_object(
            obj_base_path, "Dataset", accession_id, expected_updated_dataset_uuid
        )
        store_object_in_api_idempotent(api_client, dataset)

    # If the related Image does not exist in API add it (and its dependencies)
    try:
        image = api_client.get_image(image_uuid)
    except NotFoundException:
        specimen_uuid = "784bb7ab-30fa-4d33-b2be-00cf4a2b7b6e"
        specimen = get_expected_object(
            obj_base_path, "Specimen", accession_id, specimen_uuid
        )
        store_object_in_api_idempotent(api_client, specimen)

        creation_process_uuid = "c27f5bcc-3ee4-412e-ac21-849947a6ed4b"
        creation_process = get_expected_object(
            obj_base_path, "CreationProcess", accession_id, creation_process_uuid
        )
        store_object_in_api_idempotent(api_client, creation_process)

        image = get_expected_object(obj_base_path, "Image", accession_id, image_uuid)
        store_object_in_api_idempotent(api_client, image)


@pytest.fixture
def expected_updated_dataset_example_image_uri(image_uuid, base_path):
    obj_base_path = base_path / "test_update_example_image_uri"
    image = get_expected_object(obj_base_path, "Image", accession_id, image_uuid)
    additional_metadata = next(
        am for am in image.additional_metadata if am.name == "static_display_uri"
    )
    return additional_metadata.value["static_display_uri"]


def test_update_dataset_example_image_uri(
    old_bia_study_metadata,
    expected_updated_dataset_uuid,
    expected_updated_dataset_example_image_uri,
    reset_expected_updated_dataset,
):
    updated_datasets = update_dataset_example_image_uri(
        [accession_id], old_bia_study_metadata, api_target="local"
    )
    assert len(updated_datasets) == 1
    assert updated_datasets[0].uuid == expected_updated_dataset_uuid
    assert (
        updated_datasets[0].example_image_uri
        == expected_updated_dataset_example_image_uri
    )
