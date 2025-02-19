from typer.testing import CliRunner
from pathlib import Path
from bia_ingest import cli
from bia_ingest import persistence_strategy
from bia_ingest.biostudies import api
from bia_shared_datamodels import bia_data_model
import pytest
from bia_ingest.settings import Settings
from bia_test_data.mock_objects import (
    mock_growth_protocol,
    mock_study,
    mock_biosample,
    mock_dataset,
    mock_specimen_imaging_preparation_protocol,
    mock_image_acquisition_protocol,
    mock_annotation_method,
    mock_file_reference,
)

runner = CliRunner()


@pytest.fixture
def expected_objects() -> tuple[dict, int]:
    datasets = mock_dataset.get_dataset()
    expected_objects_dict = {
        "study": [mock_study.get_study()],
        "dataset": datasets,
        "image_acquisition_protocol": mock_image_acquisition_protocol.get_image_acquisition_protocol(),
        "specimen_imaging_preparation_protocol": mock_specimen_imaging_preparation_protocol.get_specimen_imaging_preparation_protocol(),
        "annotation_method": mock_annotation_method.get_annotation_method(),
        "protocol": mock_growth_protocol.get_growth_protocol(),
        "bio_sample": [bs for bs in mock_biosample.get_bio_sample_as_map().values()],
        "file_reference": mock_file_reference.get_file_reference(
            {
                datasets[0].uuid: "biad_v4/file_list_study_component_1.json",
                datasets[1].uuid: "biad_v4/file_list_study_component_2.json",
                datasets[2].uuid: "biad_v4/file_list_annotations_1.json",
            }
        ),
    }

    n_expected_objects = 0
    for expected_objects in expected_objects_dict.values():
        n_expected_objects += len(expected_objects)
    return expected_objects_dict, n_expected_objects


def test_cli_writes_expected_files(
    monkeypatch,
    tmp_path,
    test_submission,
    test_submission_table,
    mock_request_get,
    expected_objects,
):

    expected_objects_dict, n_expected_objects = expected_objects

    def _load_submission(accession_id: str) -> api.Submission:
        return test_submission

    def _load_submission_table_info(accession_id: str):
        return test_submission_table

    def _disk_persistance_settings(path):
        return Settings(bia_data_dir=str(path))

    monkeypatch.setattr(cli, "load_submission", _load_submission)
    monkeypatch.setattr(cli, "load_submission_table_info", _load_submission_table_info)
    monkeypatch.setattr(
        persistence_strategy, "settings", _disk_persistance_settings(tmp_path)
    )

    result = runner.invoke(
        cli.app,
        [
            "ingest",
            test_submission.accno,
            "--persistence-mode",
            "disk",
            "--process-filelist",
            "always",
        ],
    )
    assert result.exit_code == 0

    files_written = [f for f in tmp_path.rglob("*.json")]
    assert len(files_written) == n_expected_objects

    files_written_by_type = {k: [] for k in expected_objects_dict.keys()}
    file: Path
    for file in files_written:
        for key in files_written_by_type.keys():
            if file.parts[-3] == key:
                files_written_by_type[key].append(file)
                break

    for key in expected_objects_dict:
        assert len(expected_objects_dict[key]) == len(files_written_by_type[key])

    for dir_name, expected_objects in expected_objects_dict.items():
        dir_path = tmp_path / dir_name / test_submission.accno

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


def test_cli_persists_expected_documents(
    monkeypatch,
    test_submission,
    test_submission_table,
    mock_request_get,
    expected_objects,
    get_bia_api_client,
):

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
            test_submission.accno,
            "--persistence-mode",
            "local_api",
            "--process-filelist",
            "always",
        ],
    )
    assert result.exit_code == 0

    for class_name, expected_objects in expected_objects_dict.items():
        if not isinstance(expected_objects, list):
            expected_objects = [
                expected_objects,
            ]
        get_func = get_bia_api_client.__getattribute__(f"get_{class_name}")
        for expected_object in expected_objects:
            persisted_object = get_func(str(expected_object.uuid))
            # Using the model_dump_json instead of
            assert (
                persisted_object.model_dump_json() == expected_object.model_dump_json()
            )


def test_cli_find_test_study(
    monkeypatch,
    tmp_path: Path,
    mock_search_result,
):
    outfile = tmp_path.absolute() / "find_output"

    result = runner.invoke(
        cli.app,
        ["find", "new-biostudies-studies", "-o", outfile],
    )
    assert result.exit_code == 0

    with open(outfile, "r") as f:
        lines = f.readlines()

    assert lines == ["S-BIADNotYetInAPI\n"]
