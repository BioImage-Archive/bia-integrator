from typer.testing import CliRunner
from pathlib import Path
from bia_ingest import cli
from bia_ingest.biostudies.api import requests, Submission, SubmissionTable
import json
from unittest.mock import Mock
from glob import glob
from bia_shared_datamodels import bia_data_model
import pytest
from pydantic import BaseModel
from pydantic.alias_generators import to_snake 
from typing import Type


@pytest.fixture
def expected_bia_agent_objects() -> tuple[dict, int]:
    
    path_to_load = Path(__file__).parent / "data" / "example_bia_agent_study" / "expected_output"

    file_paths = glob(f"{path_to_load}/**/*.json", recursive=True)
    n_expected_objects = len(file_paths)
    expected_objects_dict = {}

    for file_name in file_paths:

        data_dict = json.loads(Path(file_name).read_text())

        object_type = data_dict["model"]["type_name"]
        bia_type: Type[BaseModel] = getattr(bia_data_model, object_type)

        if to_snake(object_type) not in expected_objects_dict:
            expected_objects_dict[to_snake(object_type)] = []
        
        expected_objects_dict[to_snake(object_type)].append(
            bia_type.model_validate(data_dict)
        )

    return expected_objects_dict, n_expected_objects


def test_cli_writes_expected_files(
    monkeypatch,
    tmp_bia_data_dir,
    test_submission_table,
    expected_bia_agent_objects,
):
    """
    Test checking a study created by the BIA Agent is ingestable.
    The two file lists have been shortened as we do not need to test every file list.
    """

    expected_objects_dict, n_expected_objects = expected_bia_agent_objects

    path_to_load = Path(__file__).parent / "data" / "example_bia_agent_study" / "input"

    def _mock_filelist_get(flist_url: str) -> dict[str, str]:
        path = path_to_load / Path(flist_url).name
        return_value = Mock()
        return_value.status_code = 200
        return_value.content = path.read_text()
        return return_value

    def _load_submission(accession_id: str) -> Submission:
        submission_path = path_to_load / "S-BIAD1492.json"
        json_data = json.loads(submission_path.read_text())
        submission = Submission.model_validate(json_data)
        return submission

    def _load_submission_table_info(accession_id: str):
        return test_submission_table

    # def _disk_persistance_settings(path):
    #     return Settings(bia_data_dir=str(path))

    monkeypatch.setattr(cli, "load_submission", _load_submission)
    monkeypatch.setattr(cli, "load_submission_table_info", _load_submission_table_info)
    # monkeypatch.setattr(
    #     persistence_strategy, "settings", _disk_persistance_settings(tmp_path)
    # )
    monkeypatch.setattr(requests, "get", _mock_filelist_get)

    runner = CliRunner()
    result = runner.invoke(
        cli.app,
        [
            "ingest",
            "S-BIAD1492",
            "--persistence-mode",
            "disk",
            "--process-filelist",
            "always",
        ],
    )
    assert result.exit_code == 0

    files_written = [f for f in tmp_bia_data_dir.rglob("*.json")]
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
        dir_path = tmp_bia_data_dir / dir_name / "S-BIAD1492"

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
