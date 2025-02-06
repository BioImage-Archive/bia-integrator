from bia_ingest.biostudies.process_submission_v4 import process_submission_v4
from bia_ingest.biostudies import api
from bia_shared_datamodels import bia_data_model

import pytest
from bia_test_data.mock_objects import (
    mock_dataset,
    mock_file_reference,
)

from bia_ingest.persistence_strategy import (
    persistence_strategy_factory,
    PersistenceStrategy,
)


def _modify_annotation_file_list(
    submission: api.Submission, file_list_path: str
) -> api.Submission:
    """Modify the path of the file list in an 'annotation' study component"""

    # Assumes there is only one annotation section and uses the first one found
    copy_of_submission = api.Submission.model_validate(submission.model_dump())
    annotation_section = next(
        s for s in copy_of_submission.section.subsections if s.type == "Annotations"
    )
    attribute = next(a for a in annotation_section.attributes if a.name == "File List")
    attribute.value = file_list_path
    return copy_of_submission


@pytest.fixture(scope="function")
def persister(test_submission, tmp_path) -> PersistenceStrategy:
    persister = persistence_strategy_factory(
        persistence_mode="disk",
        output_dir_base=str(tmp_path),
        accession_id=test_submission.accno,
    )
    return persister


@pytest.fixture
def submission_where_same_file_list_is_used_in_annotation_and_a_study_component(
    test_submission,
) -> api.Submission:
    return _modify_annotation_file_list(
        test_submission, "file_list_study_component_1.json"
    )


@pytest.fixture
def submission_where_same_file_is_referred_to_in_annotation_fl_and_a_study_component_fl(
    test_submission,
) -> api.Submission:
    # file_list_annotations_and_images has one image from study component 1 and one from study component2
    return _modify_annotation_file_list(
        test_submission, "file_list_annotations_and_images.json"
    )


@pytest.fixture
def expected_file_references_where_same_file_list_is_used_in_annotation_and_a_study_component(
    test_submission,
    mock_request_get,
) -> dict:
    datasets = mock_dataset.get_dataset()

    ds_study_component_1 = datasets[0]
    ds_study_component_2 = datasets[1]

    file_references_sc_1 = mock_file_reference.get_file_reference(
        {
            ds_study_component_1.uuid: "biad_v4/file_list_study_component_1.json",
        }
    )
    file_references_sc_2 = mock_file_reference.get_file_reference(
        {
            ds_study_component_2.uuid: "biad_v4/file_list_study_component_2.json",
        },
    )

    file_references = {f.uuid: f for f in file_references_sc_1}
    file_references.update({f.uuid: f for f in file_references_sc_2})

    return file_references


@pytest.fixture
def expected_file_references_where_same_file_is_referred_to_in_annotation_fl_and_a_study_component_fl(
    test_submission,
    mock_request_get,
    expected_file_references_where_same_file_list_is_used_in_annotation_and_a_study_component,
) -> dict:
    datasets = mock_dataset.get_dataset()

    ds_annotation = datasets[2]

    file_references_annotation = mock_file_reference.get_file_reference(
        {
            ds_annotation.uuid: "biad_v4/file_list_annotations_1.json",
        },
    )

    file_references = expected_file_references_where_same_file_list_is_used_in_annotation_and_a_study_component.copy()
    file_references.update({f.uuid: f for f in file_references_annotation})

    return file_references


def test_order_of_processing_datasets_where_same_file_list_is_used_in_annotation_and_a_study_component(
    submission_where_same_file_list_is_used_in_annotation_and_a_study_component,
    expected_file_references_where_same_file_list_is_used_in_annotation_and_a_study_component,
    ingestion_result_summary,
    persister,
    tmp_path,
):
    """
    Test that when an annotation study component and a standard study component
    have the same file list, resulting file references point to the dataset for
    the standard study component.
    """

    submission = (
        submission_where_same_file_list_is_used_in_annotation_and_a_study_component
    )
    expected_file_references = expected_file_references_where_same_file_list_is_used_in_annotation_and_a_study_component
    process_submission_v4(
        submission=submission,
        result_summary=ingestion_result_summary,
        process_files=True,
        persister=persister,
    )

    # Check expected number of file references written
    file_reference_base_path = tmp_path / "file_reference" / submission.accno
    created_file_references = [
        bia_data_model.FileReference.model_validate_json(f.read_text())
        for f in file_reference_base_path.glob("*.json")
    ]

    # Check the file references belong to the expected datasets
    assert len(created_file_references) == len(expected_file_references)
    for created_file_reference in created_file_references:
        expected_file_reference = expected_file_references[created_file_reference.uuid]
        assert (
            expected_file_reference.submission_dataset_uuid
            == created_file_reference.submission_dataset_uuid
        )


def test_order_of_processing_datasets_where_same_file_is_referred_to_in_annotation_fl_and_a_study_component_fl(
    submission_where_same_file_is_referred_to_in_annotation_fl_and_a_study_component_fl,
    expected_file_references_where_same_file_is_referred_to_in_annotation_fl_and_a_study_component_fl,
    ingestion_result_summary,
    persister,
    tmp_path,
):
    """
    Test that when the same file is in an annotation study component
    and a standard study component, the file reference created points
    to the dataset for the standard study component.
    """

    submission = submission_where_same_file_is_referred_to_in_annotation_fl_and_a_study_component_fl
    expected_file_references = expected_file_references_where_same_file_is_referred_to_in_annotation_fl_and_a_study_component_fl
    process_submission_v4(
        submission=submission,
        result_summary=ingestion_result_summary,
        process_files=True,
        persister=persister,
    )

    # Check expected number of file references written
    file_reference_base_path = tmp_path / "file_reference" / submission.accno
    created_file_references = [
        bia_data_model.FileReference.model_validate_json(f.read_text())
        for f in file_reference_base_path.glob("*.json")
    ]

    # Check the file references belong to the expected datasets
    assert len(created_file_references) == len(expected_file_references)
    for created_file_reference in created_file_references:
        expected_file_reference = expected_file_references[created_file_reference.uuid]
        assert (
            expected_file_reference.submission_dataset_uuid
            == created_file_reference.submission_dataset_uuid
        )
