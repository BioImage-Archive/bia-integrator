"""Test ImageRepresentation creation"""

from uuid import UUID
from pathlib import Path
import pytest
from bia_shared_datamodels import bia_data_model, uuid_creation, semantic_models
from bia_assign_image import image_representation
from .conftest import get_expected_object

# TODO: Create accession ID and artefacts specific to this test
ACCESSION_ID = "S-BIAD-TEST-ASSIGN-IMAGE"
EXPECTED_OBJECT_BASE_PATH = Path(__file__).parent / "test_data"
INPUT_DATA_BASE_PATH = Path(__file__).parent / "input_data"


@pytest.fixture
def study_uuid() -> UUID:
    return uuid_creation.create_study_uuid(ACCESSION_ID)


@pytest.fixture
def file_reference():
    uuid = "278ffc50-3924-4b8a-bad6-d017c503e5dd"
    return get_expected_object(
        # TODO: resolve issue with version then use INPUT_DATA_BASE_PATH
        # INPUT_DATA_BASE_PATH, "FileReference", ACCESSION_ID, uuid
        EXPECTED_OBJECT_BASE_PATH,
        "FileReference",
        ACCESSION_ID,
        uuid,
    )


@pytest.fixture
def expected_image_representation() -> bia_data_model.ImageRepresentation:
    uuid = "a0fbc4fd-2e52-424f-b8e7-6f9fd5109513"
    return get_expected_object(
        EXPECTED_OBJECT_BASE_PATH, "ImageRepresentation", ACCESSION_ID, uuid
    )


@pytest.fixture
def image() -> bia_data_model.Image:
    image_uuid = "97456be4-fd3b-4303-bff3-02b93d00bd8e"
    return get_expected_object(
        EXPECTED_OBJECT_BASE_PATH, "Image", ACCESSION_ID, image_uuid
    )


def test_create_representation_of_single_image(
    study_uuid,
    image,
    expected_image_representation,
    file_reference,
):
    created = image_representation.get_image_representation(
        study_uuid=study_uuid,
        file_references=[
            file_reference,
        ],
        image=image,
        object_creator=semantic_models.Provenance.bia_image_assignment,
    )

    assert created == expected_image_representation
