from typing import List
from uuid import UUID
from pathlib import Path
import pytest
from bia_assign_image.object_creation import image, creation_process
from bia_shared_datamodels import bia_data_model, uuid_creation

from bia_assign_image.object_creation import specimen

from .conftest import get_expected_object

ACCESSION_ID = "S-BIAD-TEST-ASSIGN-IMAGE"
EXPECTED_OBJECT_BASE_PATH = Path(__file__).parent / "test_data"


@pytest.fixture
def study_uuid():
    return uuid_creation.create_study_uuid(ACCESSION_ID)


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


@pytest.fixture()
def image_unique_str(file_references: List[bia_data_model.FileReference]) -> str:
    fr_uuids = [str(fr.uuid) for fr in file_references]
    return image.create_image_uuid_unique_string(fr_uuids)


@pytest.fixture()
def image_uuid(
    study_uuid,
    image_unique_str,
):
    return uuid_creation.create_image_uuid(study_uuid, image_unique_str)


@pytest.fixture
def specimen_imaging_preparation_protocol_uuid(
    dataset,
) -> List[UUID]:
    return dataset.additional_metadata[2].value[
        "specimen_imaging_preparation_protocol_uuid"
    ]


@pytest.fixture
def expected_image(image_uuid) -> bia_data_model.Image:
    return get_expected_object(
        EXPECTED_OBJECT_BASE_PATH, "Image", ACCESSION_ID, image_uuid
    )


@pytest.fixture
def expected_creation_process() -> bia_data_model.CreationProcess:
    expected_creation_process_uuid = "f154164e-7e6e-42f9-943e-c6d1ff0a5ba2"
    return get_expected_object(
        EXPECTED_OBJECT_BASE_PATH,
        "CreationProcess",
        ACCESSION_ID,
        expected_creation_process_uuid,
    )


@pytest.fixture
def expected_specimen() -> bia_data_model.Specimen:
    expected_specimen_uuid = "94394b72-823e-4565-8131-e4c5e60d45a7"
    return get_expected_object(
        EXPECTED_OBJECT_BASE_PATH, "Specimen", ACCESSION_ID, expected_specimen_uuid
    )


@pytest.fixture
def bio_sample_uuid(dataset) -> List[UUID]:
    return dataset.additional_metadata[3].value["bio_sample_uuid"]


def test_bia_image_with_one_file_reference(
    image_uuid, image_unique_str, dataset, expected_image, file_references
):
    created_image = image.get_image(
        image_uuid=image_uuid,
        image_uuid_unique_string=image_unique_str,
        submission_dataset_uuid=dataset.uuid,
        creation_process_uuid=expected_image.creation_process_uuid,
        file_references=file_references,
    )

    assert expected_image == created_image


def test_bia_specimen(
    study_uuid,
    image_uuid,
    specimen_imaging_preparation_protocol_uuid,
    bio_sample_uuid,
    expected_specimen,
):
    created_specimen = specimen.get_specimen(
        study_uuid,
        image_uuid,
        specimen_imaging_preparation_protocol_uuid,
        bio_sample_uuid,
    )

    assert expected_specimen == created_specimen


def test_bia_creation_process(
    study_uuid,
    image_uuid,
    expected_creation_process,
):
    # expected = mock_creation_process.get_creation_process_with_one_file_reference()
    created_creation_process = creation_process.get_creation_process(
        study_uuid=study_uuid,
        output_image_uuid=image_uuid,
        subject_specimen_uuid=expected_creation_process.subject_specimen_uuid,
        image_acquisition_protocol_uuid=expected_creation_process.image_acquisition_protocol_uuid,
    )
    assert expected_creation_process == created_creation_process
