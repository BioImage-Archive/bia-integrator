import pytest
from bia_test_data.mock_objects import (
    mock_file_reference,
    mock_dataset,
)
from bia_ingest.biostudies import submission_parsing_utils
from bia_ingest.biostudies.biostudies_default import default_file_reference
from bia_ingest.biostudies.v4 import (
    file_reference,
)
from bia_ingest.biostudies.api import File
from bia_shared_datamodels.bia_data_model import Dataset, FileReference
from bia_test_data.mock_objects.mock_object_constants import (
    study_uuid,
    study_uuid_biostudies_default,
    accession_id,
    accession_id_biostudies_default,
)
import logging

@pytest.fixture
def dataset_in_submission() -> Dataset:
    """
    Return the 2nd datast in the submission to test files lists
    """
    return mock_dataset.get_dataset()[1]


@pytest.fixture
def dataset_in_submission_biostudies_default() -> Dataset:
    return mock_dataset.get_dataset_biostudies_default()


@pytest.fixture
def biostudies_api_files():
    file_list_data = mock_file_reference.get_file_list_data(
        "biad_v4/file_list_study_component_2.json"
    )
    files_in_filelist = [File.model_validate(f) for f in file_list_data]
    return files_in_filelist


@pytest.fixture
def biostudies_default_api_files_listed():
    file_list_data = mock_file_reference.get_file_list_data(
        "default_biostudies/file_list_default.json"
    )
    files_in_filelist = [File.model_validate(f) for f in file_list_data]
    return files_in_filelist


def test_get_file_reference_for_submission_dataset(
    dataset_in_submission, biostudies_api_files, ingestion_result_summary
):
    """
    Test creation of FileReferences for dataset with file list supplied
    """
    file_path_to_file_ref_map = {}
    expected = {}
    [
        expected.update({file_ref["file_path"]: FileReference.model_validate(file_ref)})
        for file_ref in mock_file_reference.get_file_reference_data()
    ]
    created = file_reference.get_file_reference_dicts_for_submission_dataset(
        accession_id=accession_id,
        study_uuid=study_uuid,
        submission_dataset=dataset_in_submission,
        files_in_file_list=biostudies_api_files,
        file_path_to_file_ref_map=file_path_to_file_ref_map,
        result_summary=ingestion_result_summary,
    )
    assert created == expected


def test_create_file_reference_for_study_component(
    test_submission,
    caplog,
    ingestion_result_summary,
    dataset_in_submission,
    mock_request_get,
):
    caplog.set_level(logging.WARNING)
    file_path_to_file_ref_map = {}
    expected = {}
    [
        expected.update({file_ref["file_path"]: FileReference.model_validate(file_ref)})
        for file_ref in mock_file_reference.get_file_reference_data()
    ]
    created = file_reference.get_file_reference_by_dataset_as_map(
        submission=test_submission,
        study_uuid=study_uuid,
        datasets_in_submission=[dataset_in_submission],
        result_summary=ingestion_result_summary,
        file_path_to_file_ref_map=file_path_to_file_ref_map,
    )
    assert created == expected

    expected_log_message = """Number of datasets with file lists (3) is not equal to the number of datasets passed as input to this function (1). Was this deliberate?"""
    assert expected_log_message in caplog.text


def test_create_file_reference_for_study_component_when_no_matching_sc_in_file_list(
    test_submission, caplog, ingestion_result_summary
):
    """Test attempted creation of study FileReferences when study
    components in dataset do not match does in file_list
    """
    caplog.set_level(logging.WARNING)
    file_path_to_file_ref_map = {}
    dataset = mock_dataset.get_dataset()[0]
    dataset.title = "Test name not in file list"
    created = file_reference.get_file_reference_by_dataset_as_map(
        submission=test_submission,
        study_uuid=study_uuid,
        datasets_in_submission=[
            dataset,
        ],
        result_summary=ingestion_result_summary,
        file_path_to_file_ref_map=file_path_to_file_ref_map,
    )

    assert created is None

    # Check Warning message. Use form below as a 'set' is involved
    # in getting study component names - so ordering is not fixed
    expected_log_message = [
        "Intersection of titles from datasets in submission ({'Test name not in file list'}) and file lists in submission",
        "'Study Component 1'",
        "'Segmentation masks'",
        "'Study Component 2'",
        "was null - exiting",
    ]

    for expected in expected_log_message:
        assert expected in caplog.text


def test_get_direct_file_list_for_biostudies_default_submission_dataset(
    test_submission_biostudies_default_direct_files,
    dataset_in_submission_biostudies_default,
    ingestion_result_summary_biostudies_default,
):
    file_path = "default_biostudies/files_direct_default.json"
    expected = mock_file_reference.get_file_reference_data_biostudies_default(file_path)

    file_list = (
        submission_parsing_utils.find_files_and_file_lists_in_default_submission(
            test_submission_biostudies_default_direct_files,
            ingestion_result_summary_biostudies_default,
        )
    )
    created = default_file_reference.get_file_reference_dicts_for_submission_dataset(
        accession_id_biostudies_default,
        study_uuid_biostudies_default,
        dataset_in_submission_biostudies_default,
        file_list,
    )

    assert created == expected


def test_get_listed_file_list_for_biostudies_default_submission_dataset(
    biostudies_default_api_files_listed,
    dataset_in_submission_biostudies_default,
):
    file_path = "default_biostudies/file_list_default.json"
    expected = mock_file_reference.get_file_reference_data_biostudies_default(file_path)

    created = default_file_reference.get_file_reference_dicts_for_submission_dataset(
        accession_id_biostudies_default,
        study_uuid_biostudies_default,
        dataset_in_submission_biostudies_default,
        biostudies_default_api_files_listed,
    )

    assert created == expected
