"""Test FileReference creation

Test FileReference creation separately from other shared models as it
now has a different pattern of creation from other artefacts i.e.
it now needs a submitted dataset
"""

from . import utils
from bia_ingest.ingest import (
    file_reference,
)
from bia_ingest.ingest.biostudies.api import File


# Get second study component as dataset in submission
datasets_in_submission = [
    utils.get_test_experimental_imaging_dataset()[1],
]


def test_get_file_reference_for_submission_dataset(
    test_submission, ingestion_result_summary
):
    """
    Test creation of FileReferences for dataset with file list supplied
    """
    file_list_data = utils.get_test_file_list_data("file_list_study_component_2.json")
    files_in_filelist = [File.model_validate(f) for f in file_list_data]

    expected = utils.get_test_file_reference()
    created = file_reference.get_file_reference_for_submission_dataset(
        accession_id=test_submission.accno,
        submission_dataset=datasets_in_submission[0],
        files_in_file_list=files_in_filelist,
        result_summary=ingestion_result_summary,
    )
    assert created == expected


def test_create_file_reference_for_study_component(
    test_submission, caplog, ingestion_result_summary, mock_request_get
):
    expected = {datasets_in_submission[0].title_id: utils.get_test_file_reference()}
    created = file_reference.get_file_reference_by_dataset(
        test_submission,
        datasets_in_submission=datasets_in_submission,
        result_summary=ingestion_result_summary,
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

    dataset = utils.get_test_experimental_imaging_dataset()[0]
    dataset.title_id = "Test name not in file list"
    created = file_reference.get_file_reference_by_dataset(
        test_submission,
        datasets_in_submission=[
            dataset,
        ],
        result_summary=ingestion_result_summary,
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
