from typer.testing import CliRunner
from bia_ingest import cli
from bia_ingest.conversion.utils import settings
from bia_ingest import biostudies
from . import utils
from bia_shared_datamodels import bia_data_model

runner = CliRunner()

accession_id = "S-BIADTEST"

expected_objects_dict = {
    "studies": utils.get_test_study(),
    "experimental_imaging_dataset": utils.get_test_experimental_imaging_dataset(),
    "specimens": utils.get_test_specimen(),
    "biosamples": utils.get_test_biosample(),
    "image_acquisitions": utils.get_test_image_acquisition(),
    "specimen_growth_protocol": utils.get_test_specimen_growth_protocol(),
    "specimen_imaging_protocol": utils.get_test_specimen_imaging_preparation_protocol(),
}

# File references are a special case as they depend on experimental dataset
expected_file_references = utils.get_test_file_reference(
    ["file_list_study_component_1.json", "file_list_study_component_2.json"]
)
expected_objects_dict["file_references"] = expected_file_references

n_expected_objects = 0
for expected_objects in expected_objects_dict.values():
    if isinstance(expected_objects, list):
        n_expected_objects += len(expected_objects)
    else:
        n_expected_objects += 1


def test_cli_writes_expected_files(
    monkeypatch, tmp_path, test_submission, mock_request_get
):
    monkeypatch.setattr(settings, "bia_data_dir", str(tmp_path))

    def _load_submission(accession_id: str) -> biostudies.Submission:
        return test_submission

    monkeypatch.setattr(cli, "load_submission", _load_submission)

    result = runner.invoke(cli.app, ["ingest", accession_id])
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
                if dir_name == "studies":
                    created_object_path = tmp_path / "studies" / f"{accession_id}.json"
                else:
                    created_object_path = dir_path / f"{expected_object.uuid}.json"
                created_object_type = getattr(
                    bia_data_model, expected_object.model.type_name
                )
                created_object = created_object_type.model_validate_json(
                    created_object_path.read_text()
                )
                assert created_object == expected_object
