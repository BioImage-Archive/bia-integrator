"""Test ImageRepresentation creation"""

from uuid import UUID
from pathlib import Path
import pytest
from bia_shared_datamodels import bia_data_model, uuid_creation
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
    uuid = "13fd33bf-89b1-4080-9ab1-b8d804e7850b"
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
    uuid = "61259a4d-4844-4400-a7f7-c3ccaadb51d8"
    return get_expected_object(
        EXPECTED_OBJECT_BASE_PATH, "ImageRepresentation", ACCESSION_ID, uuid
    )


@pytest.fixture
def image() -> bia_data_model.Image:
    image_uuid = "aca07c38-9575-4f4e-b2cc-018b2a3e50b1"
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
    )

    assert created == expected_image_representation
