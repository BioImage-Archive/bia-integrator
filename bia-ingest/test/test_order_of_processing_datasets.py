from bia_ingest.biostudies.process_submission_v4 import process_submission_v4
from bia_ingest.biostudies import api
from bia_shared_datamodels import bia_data_model
import pytest
from bia_test_data.mock_objects import (
    mock_dataset,
    mock_file_reference,
)
from bia_ingest import persistence_strategy
from .conftest import mock_request_get

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
def persister(
    test_submission, 
    tmp_bia_data_dir, # Note this fixture is requested explicity to ensure correct ordering of fixtures (i.e. after settings are configured for tests.)
) -> persistence_strategy.PersistenceStrategy:
    persister = persistence_strategy.persistence_strategy_factory(
        persistence_mode="disk",
        accession_id=test_submission.accno,
    )
    return persister


@pytest.fixture
def submission_with_reused_file_list(
    test_submission,
) -> api.Submission:
    return _modify_annotation_file_list(
        test_submission, "file_list_study_component_1.json"
    )


@pytest.fixture
def submission_with_file_lists_with_some_identical_file_paths(
    test_submission,
) -> api.Submission:
    # file_list_annotations_and_images has one image from study component 1 and one from study component2
    return _modify_annotation_file_list(
        test_submission, "file_list_annotations_and_images.json"
    )


@pytest.fixture
def study_component_file_references_only() -> dict:
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
def study_component_and_unique_annotation_file_references(
    study_component_file_references_only,
) -> dict:
    datasets = mock_dataset.get_dataset()

    ds_annotation = datasets[2]

    file_references_annotation = mock_file_reference.get_file_reference(
        {
            ds_annotation.uuid: "biad_v4/file_list_annotations_1.json",
        },
    )

    file_references = study_component_file_references_only.copy()
    file_references.update({f.uuid: f for f in file_references_annotation})

    return file_references


@pytest.mark.usefixtures(mock_request_get.__name__)
@pytest.mark.parametrize(
    "submission_fixture, expected_file_references_fixture",
    [
        (submission_with_reused_file_list, study_component_file_references_only),
        (
            submission_with_file_lists_with_some_identical_file_paths,
            study_component_and_unique_annotation_file_references,
        ),
    ],
)
def test_process_submission_v4_prefers_study_component_dataset_when_creating_file_references(
    submission_fixture,
    expected_file_references_fixture,
    request,
    ingestion_result_summary,
    tmp_bia_data_dir,
    persister,

):
    """
    Tests that when file references with the same file path (i.e. with the same uuid) are created
    from either:
        - a submission where a annotation study component and a standard study component have the same file list
        - a submission where the files lists from an annotation study component and a standard study component have the same file paths
    In both cases we prefer that the file reference created point to the dataset created from the standard study component.
    """

    submission = request.getfixturevalue(submission_fixture.__name__)
    expected_file_references = request.getfixturevalue(
        expected_file_references_fixture.__name__
    )

    process_submission_v4(
        submission=submission,
        result_summary=ingestion_result_summary,
        process_files=True,
        persister=persister,
    )

    # Check expected number of file references written
    file_reference_base_path = tmp_bia_data_dir / "file_reference" / submission.accno
    created_file_references = [
        bia_data_model.FileReference.model_validate_json(f.read_text())
        for f in file_reference_base_path.glob("*.json")
    ]

    # Check the file references belong to the expected datasets
    assert len(created_file_references) == len(expected_file_references)
    for created_file_reference in created_file_references:
        expected_file_reference = expected_file_references[created_file_reference.uuid]
        assert expected_file_reference == created_file_reference
