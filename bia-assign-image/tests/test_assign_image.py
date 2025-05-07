from typing import List
from uuid import UUID
from pathlib import Path
import pytest
from bia_assign_image import image, specimen, creation_process
from bia_shared_datamodels import bia_data_model

from .conftest import get_expected_object

ACCESSION_ID = "S-BIAD-TEST-ASSIGN-IMAGE"
EXPECTED_OBJECT_BASE_PATH = Path(__file__).parent / "test_data"


@pytest.fixture
def dataset(private_client) -> bia_data_model.Dataset:
    # Return Dataset for this test

    study = private_client.search_study_by_accession(ACCESSION_ID)
    dataset = private_client.get_dataset_linking_study(study.uuid, page_size=1)

    return dataset[0]


@pytest.fixture
def image_acquisition_protocol(
    dataset,
) -> List[UUID]:
    return dataset.additional_metadata[1].value["image_acquisition_protocol_uuid"]


@pytest.fixture
def file_references(
    private_client,
    dataset,
) -> List[bia_data_model.FileReference]:
    return private_client.get_file_reference_linking_dataset(dataset.uuid, page_size=1)


@pytest.fixture
def specimen_imaging_preparation_protocol_uuid(
    dataset,
) -> List[UUID]:
    return dataset.additional_metadata[2].value[
        "specimen_imaging_preparation_protocol_uuid"
    ]


@pytest.fixture
def expected_image() -> bia_data_model.Image:
    expected_image_uuid = "aca07c38-9575-4f4e-b2cc-018b2a3e50b1"
    return get_expected_object(
        EXPECTED_OBJECT_BASE_PATH, "Image", ACCESSION_ID, expected_image_uuid
    )


@pytest.fixture
def expected_creation_process() -> bia_data_model.CreationProcess:
    expected_creation_process_uuid = "a289db7f-5034-43ef-a2ac-4d74ed3d0dcc"
    return get_expected_object(
        EXPECTED_OBJECT_BASE_PATH,
        "CreationProcess",
        ACCESSION_ID,
        expected_creation_process_uuid,
    )


@pytest.fixture
def expected_specimen() -> bia_data_model.Specimen:
    expected_specimen_uuid = "315c82ae-1a74-465f-890d-754beedab6a7"
    return get_expected_object(
        EXPECTED_OBJECT_BASE_PATH, "Specimen", ACCESSION_ID, expected_specimen_uuid
    )


@pytest.fixture
def bio_sample_uuid(dataset) -> List[UUID]:
    return dataset.additional_metadata[3].value["bio_sample_uuid"]


def test_bia_image_with_one_file_reference(dataset, expected_image, file_references):
    created_image = image.get_image(
        study_uuid=dataset.submitted_in_study_uuid,
        submission_dataset_uuid=dataset.uuid,
        creation_process_uuid=expected_image.creation_process_uuid,
        file_references=file_references,
    )

    assert expected_image == created_image


def test_bia_specimen(
    dataset,
    specimen_imaging_preparation_protocol_uuid,
    bio_sample_uuid,
    expected_specimen,
    expected_image,
):
    created_specimen = specimen.get_specimen(
        dataset.submitted_in_study_uuid,
        expected_image.uuid,
        [
            specimen_imaging_preparation_protocol_uuid,
        ],
        [
            bio_sample_uuid,
        ],
    )

    assert expected_specimen == created_specimen


def test_bia_creation_process(dataset, expected_creation_process, expected_image):
    # expected = mock_creation_process.get_creation_process_with_one_file_reference()
    created_creation_process = creation_process.get_creation_process(
        study_uuid=dataset.submitted_in_study_uuid,
        output_image_uuid=expected_image.uuid,
        subject_specimen_uuid=expected_creation_process.subject_specimen_uuid,
        image_acquisition_protocol_uuid=expected_creation_process.image_acquisition_protocol_uuid,
    )
    assert expected_creation_process == created_creation_process
