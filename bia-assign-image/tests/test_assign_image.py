import pytest
from bia_assign_image import image, specimen, creation_process
from .mock_objects import mock_image, mock_specimen, mock_creation_process
from bia_ingest import persistence_strategy
from bia_test_data.mock_objects.utils import accession_id
from bia_test_data.mock_objects import mock_dataset, mock_file_reference
from bia_shared_datamodels import bia_data_model

@pytest.fixture
def persister(tmpdir):
    """
        Create disk persister to a temporary directory and dump
        the mock dataset objects needed for test in these. Return
        the persister
    """
    persister = persistence_strategy.persistence_strategy_factory(
        "disk",
        accession_id=accession_id,
        output_dir_base=str(tmpdir)
    )
    persister.persist(mock_dataset.get_dataset())
    yield persister

@pytest.fixture
def dataset_for_study_component_2() -> bia_data_model.Dataset:
    return mock_dataset.get_dataset()[1]

def test_bia_image_with_one_file_reference(dataset_for_study_component_2):
    expected = mock_image.get_image_with_one_file_reference()
    created = image.get_image(
        submission_dataset_uuid=dataset_for_study_component_2.uuid,
        creation_process_uuid=expected.creation_process_uuid,
        file_references=mock_file_reference.get_file_reference()[:1],
    )

    assert expected == created

def test_bia_specimen(dataset_for_study_component_2):
    expected= mock_specimen.get_specimen_for_image_with_one_file_reference()
    created = specimen.get_specimen(
        mock_image.get_image_with_one_file_reference().uuid, 
        dataset_for_study_component_2,
    )

    assert expected == created

def test_bia_creation_process(dataset_for_study_component_2):
    expected = mock_creation_process.get_creation_process_with_one_file_reference()
    input_image_uuid = mock_image.get_image_with_one_file_reference().uuid
    subject_specimen_uuid = mock_specimen.get_specimen_for_image_with_one_file_reference().uuid
    created = creation_process.get_creation_process(
        input_image_uuid, dataset_for_study_component_2, subject_specimen_uuid
    )
    assert expected == created