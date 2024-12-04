import pytest
from bia_assign_image import image, specimen
from .mock_objects import mock_image, mock_specimen, mock_creation_process
from bia_ingest import persistence_strategy
from bia_test_data.mock_objects.utils import accession_id
from bia_test_data.mock_objects import mock_dataset
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


def test_bia_image_with_one_file_reference():
    expected_image = mock_image.get_image_with_one_file_reference()
    created_image = image.get_image(
        submission_dataset_uuid=mock_image.dataset.uuid,
        creation_process_uuid=expected_image.creation_process_uuid,
        original_file_reference_uuid=expected_image.original_file_reference_uuid,
    )

    assert expected_image == created_image

def test_bia_specimen(persister):
    expected= mock_specimen.get_specimen_for_image_with_one_file_reference()
    created = specimen.get_specimen(
        mock_image.get_image_with_one_file_reference(), 
        persister
    )

    assert expected == created

def test_bia_creation_process(persister):
    expected = mock_creation_process.get_creation_process_with_one_file_reference()
    assert expected