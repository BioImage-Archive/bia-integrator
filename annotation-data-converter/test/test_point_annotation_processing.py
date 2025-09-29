import os
import pathlib
import pytest_check as check

from typer.testing import CliRunner
from annotation_data_converter.cli import annotation_data_convert

runner = CliRunner()


def test_starfile_convert_to_neuroglancer(data_in_api, tmpdir):

    commands = [
        "-p",
        "proposals/point_annotations/test_proposal.json",
        "-od",
        tmpdir,
        "-am",
        "local_api",
    ]

    result = runner.invoke(annotation_data_convert, commands)
    assert result.exit_code == 0

    expected_folders = [
        "35c60bfa-6f41-46ef-b058-7b2207d681af_f0444894-c673-458c-a07d-fd63994fce1e",
        "15402ddb-30db-459b-9e2d-3a16479de8c4_f0444894-c673-458c-a07d-fd63994fce1e",
        "dc76699b-a366-4062-8084-e0cab772fa36_f0444894-c673-458c-a07d-fd63994fce1e",
    ]

    for folder in expected_folders:
        folder_path = tmpdir / folder
        check.is_true(os.path.exists(folder_path))
        check.is_true(os.path.exists(folder_path / "info"))
        check.is_true(len(os.listdir(folder_path/"by_id")) > 0)
        check.is_true(len(os.listdir(folder_path/"spatial0")) > 0)


