"""Test core functions of script to map image related artefacts to 2025/04 version of models"""

import os
from pathlib import Path
import json
import pytest
from bia_shared_datamodels import bia_data_model
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
    contains_displayable_image_representation,
)

# Use details from an actual study
accession_id = "S-BIAD609"
empiar_accession_id = "EMPIAR-10326"


@pytest.fixture
def base_path() -> Path:
    return Path(__file__).parent / "test_data" / "migrate_to_2025_04_models"


@pytest.fixture
def file_reference_mapping(base_path) -> dict:
    file_reference_mapping_path = (
        base_path / "pre_2025_04_models" / "test-file-reference-mapping.json"
    )
    file_reference_mappings = json.loads(file_reference_mapping_path.read_text())
    return list(file_reference_mappings.values())[0]


@pytest.fixture
def file_reference_mapping_empiar(base_path) -> dict:
    file_reference_mapping_path = (
        base_path / "pre_2025_04_models" / "test-file-reference-mapping-empiar.json"
    )
    file_reference_mappings = json.loads(file_reference_mapping_path.read_text())
    return list(file_reference_mappings.values())[0]


@pytest.fixture
def file_reference_mapping_no_displayable_images(base_path) -> dict:
    file_reference_mapping_path = (
        base_path
        / "pre_2025_04_models"
        / "test-file-reference-mapping-no-displayable-images.json"
    )
    file_reference_mappings = json.loads(file_reference_mapping_path.read_text())
    return list(file_reference_mappings.values())[0]


@pytest.fixture
def expected_2025_04_image(base_path) -> bia_data_model.Image:
    obj_path = base_path / "2025_04_models"
    uuid = "71fb4f2d-6cff-495f-ae21-d1c6ab068de7"
    return get_expected_object(obj_path, "Image", accession_id, uuid)


@pytest.fixture
def expected_2025_04_image_empiar(base_path) -> bia_data_model.Image:
    obj_path = base_path / "2025_04_models"
    uuid = "0c51b3ea-256d-43c6-a648-26ed787a6b62"
    return get_expected_object(obj_path, "Image", empiar_accession_id, uuid)


@pytest.fixture
def expected_2025_04_representation_of_image_uploaded_by_submitter(
    base_path,
) -> bia_data_model.ImageRepresentation:
    obj_path = base_path / "2025_04_models"
    uuid = "87f9f5e7-473e-4c81-afbf-1dcd148492f4"
    return get_expected_object(obj_path, "ImageRepresentation", accession_id, uuid)


@pytest.fixture
def expected_2025_04_representation_of_image_uploaded_by_submitter_empiar(
    base_path,
) -> bia_data_model.ImageRepresentation:
    obj_path = base_path / "2025_04_models"
    uuid = "8dd18449-7eea-4e65-b6d7-58cb16a733f8"
    return get_expected_object(
        obj_path, "ImageRepresentation", empiar_accession_id, uuid
    )


@pytest.fixture
def expected_2025_04_representation_of_image_converted_to_ome_zarr(
    base_path,
) -> bia_data_model.ImageRepresentation:
    obj_path = base_path / "2025_04_models"
    uuid = "cca7f5db-2c46-4234-8d48-eb431a733007"
    return get_expected_object(obj_path, "ImageRepresentation", accession_id, uuid)


@pytest.fixture
def expected_2025_04_representation_of_image_converted_to_ome_zarr_empiar(
    base_path,
) -> list[bia_data_model.ImageRepresentation]:
    obj_path = base_path / "2025_04_models"
    uuids = [
        "c7a0a5d2-0866-4cf7-8ae5-434b8562f888",
        "a7f977ed-721c-4bb7-92b8-e14a57615477",
    ]
    expected_objects = []
    for uuid in uuids:
        expected_objects.append(
            get_expected_object(
                obj_path, "ImageRepresentation", empiar_accession_id, uuid
            )
        )
    return expected_objects


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
    # The versions may be different depending on no. of
    # times the test has been run - so don't compare version
    mapped_artefacts["image"].version = expected_2025_04_image.version
    assert mapped_artefacts["image"] == expected_2025_04_image
    assert (
        mapped_artefacts["representation_of_image_uploaded_by_submitter"]
        == expected_2025_04_representation_of_image_uploaded_by_submitter
    )
    assert len(mapped_artefacts["representation_of_image_converted_to_ome_zarr"]) == 1
    assert (
        mapped_artefacts["representation_of_image_converted_to_ome_zarr"][0]
        == expected_2025_04_representation_of_image_converted_to_ome_zarr
    )

    # Test if Dataset details in Image are correct?

    # Test if Creation process details in Image are correct?


def test_identification_of_mappings_with_no_displayable_image_representations(
    file_reference_mapping,
    file_reference_mapping_no_displayable_images,
):
    displayable_image_representations = contains_displayable_image_representation(
        file_reference_mapping_no_displayable_images,
    )
    assert not displayable_image_representations

    displayable_image_representations = contains_displayable_image_representation(
        file_reference_mapping,
    )
    assert displayable_image_representations


def test_map_image_related_artefacts_to_2025_04_models_empiar(
    file_reference_mapping_empiar,
    expected_2025_04_image_empiar,
    expected_2025_04_representation_of_image_converted_to_ome_zarr_empiar,
    expected_2025_04_representation_of_image_uploaded_by_submitter_empiar,
):
    mapped_artefacts = map_image_related_artefacts_to_2025_04_models(
        file_reference_mapping_empiar,
        empiar_accession_id,
        api_target="local",
    )
    # The versions may be different depending on no. of
    # times the test has been run - so don't compare version
    mapped_artefacts["image"].version = expected_2025_04_image_empiar.version
    assert mapped_artefacts["image"] == expected_2025_04_image_empiar
    assert (
        mapped_artefacts["representation_of_image_uploaded_by_submitter"]
        == expected_2025_04_representation_of_image_uploaded_by_submitter_empiar
    )

    # For EMPIAR entries we are returning lists
    n_expected_image_representations = len(
        expected_2025_04_representation_of_image_converted_to_ome_zarr_empiar
    )
    n_mapped_image_representations = len(
        mapped_artefacts["representation_of_image_converted_to_ome_zarr"]
    )
    assert n_expected_image_representations == n_mapped_image_representations

    for expected, mapped in zip(
        expected_2025_04_representation_of_image_converted_to_ome_zarr_empiar,
        mapped_artefacts["representation_of_image_converted_to_ome_zarr"],
    ):
        mapped.version = expected.version
        assert mapped == expected
