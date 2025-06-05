import os
from pathlib import Path
import json
import pytest
from bia_assign_image.api_client import get_local_bia_api_client, store_object_in_api_idempotent

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
    update_dataset_example_image_uri
)

accession_id = "S-BIAD-MAP-IMAGE-RELATED-ARTEFACTS-TO-2025-04-MODELS-TEST"

@pytest.fixture
def base_path() -> Path:
    return Path(__file__).parent / "test_data" / "migrate_to_2025_04_models"

@pytest.fixture
def old_bia_study_metadata(base_path) -> dict:
    old_bia_study_metadata_path = (
        base_path / "pre_2025_04_models" / "bia-study-metadata.json"
    )
    old_bia_study_metadata = json.loads(old_bia_study_metadata_path.read_text())
    return old_bia_study_metadata

@pytest.fixture
def expected_updated_dataset_uuid():
    return "df381b39-0768-493e-90ed-7c653f012f1f"

@pytest.fixture
def expected_updated_dataset_example_image_uri():
    return "https://updated_example_image_uri"

@pytest.fixture
def reset_dataset_example_image_uri(expected_updated_dataset_uuid):
    """Reset the dataset example image uri to ba an empty string"""
    api_client = get_local_bia_api_client()
    dataset = api_client.get_dataset(expected_updated_dataset_uuid)
    dataset.example_image_uri = []
    store_object_in_api_idempotent(api_client, dataset)

def test_update_dataset_example_image_uri(
        reset_dataset_example_image_uri,
        old_bia_study_metadata,
        expected_updated_dataset_uuid,
        expected_updated_dataset_example_image_uri,
):
    updated_datasets = update_dataset_example_image_uri(accession_id, old_bia_study_metadata, api_target="local")
    assert(len(updated_datasets) == 1)
    assert updated_datasets[0].uuid == expected_updated_dataset_uuid
    assert updated_datasets[0].example_image_uri == expected_updated_dataset_example_image_uri

