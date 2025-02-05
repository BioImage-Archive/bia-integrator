from pathlib import Path
import json
from bia_ingest.biostudies.process_submission_v4 import process_submission_v4
from bia_ingest.biostudies import api
from bia_shared_datamodels import bia_data_model

import pytest
from bia_test_data.mock_objects import (
    mock_dataset,
    mock_file_reference,
)
from bia_test_data import bia_test_data_dir

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


@pytest.fixture
def test_submission_annotations_and_images_file_list() -> api.Submission:
    submission_path = (
        bia_test_data_dir
        / "biad_v4"
        / "S-BIADTEST_ANNOTATIONS_AND_IMAGES_FILE_LIST.json"
    )
    json_data = json.loads(submission_path.read_text())
    submission = api.Submission.model_validate(json_data)
    return submission


@pytest.fixture()
def output_dir_base(tmp_path):
    return Path(tmp_path)


@pytest.fixture
def persister(test_submission, output_dir_base) -> PersistenceStrategy:
    persister = persistence_strategy_factory(
        persistence_mode="disk",
        output_dir_base=str(output_dir_base),
        accession_id=test_submission.accno,
    )
    return persister


@pytest.fixture
def test_parameters(
    test_submission,
    mock_request_get,
) -> dict:
    datasets = mock_dataset.get_dataset()

    ds_study_component_1 = datasets[0]
    ds_study_component_2 = datasets[1]
    ds_annotation = datasets[2]

    # Get file references from standard test file lists
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
    file_references_annotation = mock_file_reference.get_file_reference(
        {
            ds_annotation.uuid: "biad_v4/file_list_annotations_1.json",
        },
    )

    file_references_file_list_repeated = {f.uuid: f for f in file_references_sc_1}
    file_references_file_list_repeated.update({f.uuid: f for f in file_references_sc_2})
    file_references_test_submission = file_references_file_list_repeated.copy()
    file_references_test_submission.update(
        {f.uuid: f for f in file_references_annotation}
    )

    # Get file references from mixed annotations and images file list and
    # override submission_dataset_uuid to point to respective study
    # component datasets
    #
    # We could have used file_references_test_submission, but compute explicitly
    # in case things change in future
    file_references_annotations_and_images = mock_file_reference.get_file_reference(
        {
            ds_annotation.uuid: "biad_v4/file_list_annotations_and_images.json",
        },
    )
    for file_reference in file_references_annotations_and_images:
        if file_reference.file_path == "study_component1/im06.png":
            file_reference.submission_dataset_uuid = ds_study_component_1.uuid
            file_reference.attribute = file_references_test_submission[
                file_reference.uuid
            ].attribute
        elif file_reference.file_path == "study_component2/im06.png":
            file_reference.submission_dataset_uuid = ds_study_component_2.uuid
            file_reference.attribute = file_references_test_submission[
                file_reference.uuid
            ].attribute
    file_references_mixed = file_references_file_list_repeated.copy()
    file_references_mixed.update(
        {f.uuid: f for f in file_references_annotations_and_images}
    )

    test_submission_sc_use_same_file_list = _modify_annotation_file_list(
        test_submission, "file_list_study_component_1.json"
    )
    test_submission_annotations_and_images_file_list = _modify_annotation_file_list(
        test_submission, "file_list_annotations_and_images.json"
    )
    return {
        "test_submission": {
            "submission": test_submission,
            "expected_file_references": file_references_test_submission,
        },
        "test_submission_sc_use_same_file_list": {
            "submission": test_submission_sc_use_same_file_list,
            "expected_file_references": file_references_file_list_repeated,
        },
        "test_submission_annotations_and_images_file_list": {
            "submission": test_submission_annotations_and_images_file_list,
            "expected_file_references": file_references_mixed,
        },
    }


@pytest.mark.parametrize(
    "submission_to_process",
    (
        "test_submission",
        "test_submission_sc_use_same_file_list",
        "test_submission_annotations_and_images_file_list",
    ),
)
def test_order_of_processing_datasets(
    submission_to_process,
    test_parameters,
    ingestion_result_summary,
    persister,
    output_dir_base,
):
    """Test normal dataset trumps annotation ds in file Reference

    Test that normal dataset is pointed to by file references
    when two study components (one for annotations) have the
    same file list.
    """

    submission = test_parameters[submission_to_process]["submission"]
    process_submission_v4(
        submission=submission,
        result_summary=ingestion_result_summary,
        process_files=True,
        persister=persister,
    )

    # Check expected number of file references written
    file_reference_base_path = output_dir_base / "file_reference" / submission.accno
    created_file_references = [
        bia_data_model.FileReference.model_validate_json(f.read_text())
        for f in file_reference_base_path.glob("*.json")
    ]

    # Check the file references belong to the expected datasets
    expected_file_references = test_parameters[submission_to_process][
        "expected_file_references"
    ]
    assert len(created_file_references) == len(expected_file_references)
    for created_file_reference in created_file_references:
        expected_file_reference = expected_file_references[created_file_reference.uuid]
        assert expected_file_reference == created_file_reference
