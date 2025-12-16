import os
import pytest_check as check

from typer.testing import CliRunner
from annotation_data_converter.cli import annotation_data_convert

runner = CliRunner()


def test_starfile_convert_to_neuroglancer(data_in_api, tmp_bia_data_dir):

    commands = [
        "convert", 
        "-p",
        "proposals/point_annotations/test_proposal.json",
        "-od",
        str(tmp_bia_data_dir), 
        "-om",
        "local",
        "-am",
        "local_api",
    ]

    result = runner.invoke(annotation_data_convert, commands)
    assert result.exit_code == 0

    # The actual path structure is: annotations/{accession_id}/{image_uuid}/{annotation_data_uuid}
    # Where accession_id is "point_annotations" and image_uuid is "f0444894-c673-458c-a07d-fd63994fce1e"
    image_uuid = "f0444894-c673-458c-a07d-fd63994fce1e"
    base_path = tmp_bia_data_dir / "annotations" / "point_annotations" / image_uuid
    
    expected_annotation_uuids = [
        "35c60bfa-6f41-46ef-b058-7b2207d681af",
        "15402ddb-30db-459b-9e2d-3a16479de8c4",
        "dc76699b-a366-4062-8084-e0cab772fa36",
    ]

    for annotation_uuid in expected_annotation_uuids:
        folder_path = base_path / annotation_uuid
        check.is_true(os.path.exists(folder_path), msg=f"Folder {folder_path} should exist")
        check.is_true(os.path.exists(folder_path / "info"), msg=f"Info file should exist in {folder_path}")
        check.is_true(len(os.listdir(folder_path/"by_id")) > 0, msg=f"by_id should have contents in {folder_path}")
        check.is_true(len(os.listdir(folder_path/"spatial0")) > 0, msg=f"spatial0 should have contents in {folder_path}")