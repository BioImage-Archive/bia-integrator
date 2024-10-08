from typer.testing import CliRunner
from bia_ingest import cli
from bia_ingest.ingest.generic_conversion_utils import settings
from bia_ingest.ingest.biostudies import api
from . import utils
from bia_shared_datamodels import bia_data_model
import pytest

runner = CliRunner()

accession_id = "S-BIADTEST"


@pytest.fixture
def expected_objects():
    expected_objects_dict = {
        "study": utils.get_test_study(),
        "experimental_imaging_dataset": utils.get_test_experimental_imaging_dataset(),
        "specimen": utils.get_test_specimen(),
        "bio_sample": utils.get_test_biosample(),
        "image_acquisition": utils.get_test_image_acquisition(),
        "specimen_growth_protocol": utils.get_test_specimen_growth_protocol(),
        "specimen_imaging_preparation_protocol": utils.get_test_specimen_imaging_preparation_protocol(),
        "annotation_method": utils.get_test_annotation_method(),
        "image_annotation_dataset": utils.get_test_image_annotation_dataset(),
    }

    # File references are a special case as they depend on experimental dataset
    expected_file_references = utils.get_test_file_reference(
        ["file_list_study_component_1.json", "file_list_study_component_2.json"]
    )
    expected_objects_dict["file_reference"] = expected_file_references

    n_expected_objects = 0
    for expected_objects in expected_objects_dict.values():
        if isinstance(expected_objects, list):
            n_expected_objects += len(expected_objects)
        else:
            n_expected_objects += 1

    return expected_objects_dict, n_expected_objects


def test_cli_writes_expected_files(
    monkeypatch, tmp_path, test_submission, test_submission_table, mock_request_get, expected_objects
):
    monkeypatch.setattr(settings, "bia_data_dir", str(tmp_path))

    expected_objects_dict, n_expected_objects = expected_objects

    def _load_submission(accession_id: str) -> api.Submission:
        return test_submission

    def _load_submission_table_info(accession_id: str):
        return test_submission_table
    
    monkeypatch.setattr(cli, "load_submission", _load_submission)
    monkeypatch.setattr(cli, "load_submission_table_info", _load_submission_table_info)


    result = runner.invoke(
        cli.app,
        [
            "ingest",
            accession_id,
            "--persistence-mode",
            "disk",
            "--process-filelist",
            "always",
        ],
    )
    assert result.exit_code == 0

    files_written = [f for f in tmp_path.rglob("*.json")]

    assert len(files_written) == n_expected_objects

    for dir_name, expected_objects in expected_objects_dict.items():
        dir_path = tmp_path / dir_name / accession_id

        if not isinstance(expected_objects, list):
            expected_objects = [
                expected_objects,
            ]
        for expected_object in expected_objects:
            created_object_path = dir_path / f"{expected_object.uuid}.json"
            created_object_type = getattr(
                bia_data_model, expected_object.model.type_name
            )
            created_object = created_object_type.model_validate_json(
                created_object_path.read_text()
            )
            assert created_object == expected_object
