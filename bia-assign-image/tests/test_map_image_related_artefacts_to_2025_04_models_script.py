"""Test core functions of script to map image related artefacts to 2025/04 version of models"""

import os
from pathlib import Path
import json
import pytest
from bia_shared_datamodels import bia_data_model, semantic_models
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
    map_image_related_artefacts_to_2025_04_models,
)

# Use details from an actual study
accession_id = "S-BIAD609"

@pytest.fixture
def base_path() -> Path:
    return Path(__file__).parent / "test_data" / "migrate_to_2025_04_models"

@pytest.fixture
def file_reference_mapping(base_path) -> dict:
    file_reference_mapping_path = base_path / "pre_2025_04_models" / "test-file-reference-mapping.json"
    file_reference_mappings = json.loads(file_reference_mapping_path.read_text())
    return list(file_reference_mappings.values())[0]


@pytest.fixture
def expected_2025_04_image(base_path) -> bia_data_model.Image:
    obj_path = base_path / "2025_04_models"
    uuid = "71fb4f2d-6cff-495f-ae21-d1c6ab068de7"
    return get_expected_object(obj_path, "Image", accession_id, uuid)

@pytest.fixture
def expected_2025_04_representation_of_image_uploaded_by_submitter(
    base_path
) -> bia_data_model.ImageRepresentation:
    obj_path = base_path / "2025_04_models"
    uuid = "87f9f5e7-473e-4c81-afbf-1dcd148492f4"
    return get_expected_object(obj_path, "ImageRepresentation", accession_id, uuid)

@pytest.fixture
def expected_2025_04_representation_of_image_converted_to_ome_zarr(
    base_path
) -> bia_data_model.ImageRepresentation:
    obj_path = base_path / "2025_04_models"
    uuid = "2a8ecffd-6690-494f-acbb-81fb94f2df30"
    return get_expected_object(obj_path, "ImageRepresentation", accession_id, uuid)


def test_map_image_related_artefacts_to_2025_04_models(
    file_reference_mapping,
    expected_2025_04_image,
    expected_2025_04_representation_of_image_converted_to_ome_zarr,
    expected_2025_04_representation_of_image_uploaded_by_submitter,
):
    mapped_artefacts = map_image_related_artefacts_to_2025_04_models(
        file_reference_mapping, 
        accession_id,
        api_target="local",
    )
    assert mapped_artefacts["image"] == expected_2025_04_image
    assert mapped_artefacts["representation_of_image_uploaded_by_submitter"] == expected_2025_04_representation_of_image_uploaded_by_submitter
    assert mapped_artefacts["representation_of_image_converted_to_ome_zarr"] == expected_2025_04_representation_of_image_converted_to_ome_zarr


    # Test if Dataset details in Image are correct?

    # Test if Creation process details in Image are correct?