from typing import List
from uuid import UUID
import pytest
from bia_assign_image import image, specimen, creation_process
from bia_test_data.mock_objects import (
    mock_dataset,
    mock_file_reference,
    mock_image,
    mock_specimen,
    mock_creation_process,
)
from bia_shared_datamodels import bia_data_model


@pytest.fixture
def dataset_for_study_component_2() -> bia_data_model.Dataset:
    # Return Dataset for the study component 2 in the Test
    # submission that has file references corresponding to
    # those used to create mock object.
    return mock_dataset.get_dataset()[1]


@pytest.fixture
def image_acquisition_protocol_uuid_for_sc2(
    dataset_for_study_component_2,
) -> List[UUID]:
    return dataset_for_study_component_2.attribute[1].value[
        "image_acquisition_protocol_uuid"
    ]


@pytest.fixture
def specimen_imaging_preparation_protocol_uuid_for_sc2(
    dataset_for_study_component_2,
) -> List[UUID]:
    return dataset_for_study_component_2.attribute[2].value[
        "specimen_imaging_preparation_protocol_uuid"
    ]


@pytest.fixture
def bio_sample_uuid_for_sc2(dataset_for_study_component_2) -> List[UUID]:
    return dataset_for_study_component_2.attribute[3].value["bio_sample_uuid"]


def test_bia_image_with_one_file_reference(dataset_for_study_component_2):
    expected = mock_image.get_image_with_one_file_reference()
    created = image.get_image(
        submission_dataset_uuid=dataset_for_study_component_2.uuid,
        creation_process_uuid=expected.creation_process_uuid,
        file_references=mock_file_reference.get_file_reference()[:1],
    )

    assert expected == created


def test_bia_specimen(
    specimen_imaging_preparation_protocol_uuid_for_sc2,
    bio_sample_uuid_for_sc2,
):
    expected = mock_specimen.get_specimen_for_image_with_one_file_reference()
    created = specimen.get_specimen(
        mock_image.get_image_with_one_file_reference().uuid,
        specimen_imaging_preparation_protocol_uuid_for_sc2,
        bio_sample_uuid_for_sc2,
    )

    assert expected == created


def test_bia_creation_process(
    image_acquisition_protocol_uuid_for_sc2,
):
    expected = mock_creation_process.get_creation_process_with_one_file_reference()
    output_image_uuid = mock_image.get_image_with_one_file_reference().uuid
    subject_specimen_uuid = (
        mock_specimen.get_specimen_for_image_with_one_file_reference().uuid
    )
    created = creation_process.get_creation_process(
        output_image_uuid,
        subject_specimen_uuid,
        image_acquisition_protocol_uuid_for_sc2,
    )
    assert expected == created
