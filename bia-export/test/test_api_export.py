from typer.testing import CliRunner
from pathlib import Path
import pytest
from bia_export.cli import (
    app,
    DEFAULT_WEBSITE_STUDY_FILE_NAME,
    DEFAULT_WEBSITE_IMAGE_FILE_NAME,
    DEFAULT_WEBSITE_DATASET_FOR_IMAGE_FILE_NAME,
)
import json
import os

runner = CliRunner()


# Note that pytest fixture data_in_api is unused in test code,
# but requested in order to guarentee that data is in the test api before running the test
def test_cli_export_export_all_data_contains_at_least_expected_objects(
    tmp_path: Path, data_in_api
):

    outpath = tmp_path.resolve()

    result = runner.invoke(
        app,
        [
            "website",
            "all",
            "-o",
            outpath,
        ],
    )

    assert result.exit_code == 0
    assert len(os.listdir(tmp_path)) == 3

    def check_file_contains_expected_object(outfile: Path, expected_output: Path):
        with open(outfile, "r") as f:
            json_result = json.load(f)

        with open(expected_output) as f:
            json_expected = json.load(f)

        for key, value in json_expected.items():
            assert key in json_result
            assert value == json_result[key]

    check_file_contains_expected_object(
        outpath.joinpath(DEFAULT_WEBSITE_STUDY_FILE_NAME),
        Path(__file__).parent.joinpath("output_data/bia-study-metadata.json"),
    )

    check_file_contains_expected_object(
        outpath.joinpath(DEFAULT_WEBSITE_IMAGE_FILE_NAME),
        Path(__file__).parent.joinpath("output_data/bia-image-metadata.json"),
    )

    check_file_contains_expected_object(
        outpath.joinpath(DEFAULT_WEBSITE_DATASET_FOR_IMAGE_FILE_NAME),
        Path(__file__).parent.joinpath("output_data/bia-dataset-metadata-for-images.json"),
    )


# Note that pytest fixture data_in_api is unused in test code,
# but requested in order to guarentee that data is in the test api before running the test
def test_cli_export_website_studies(tmp_path: Path, data_in_api):
    expected_output = Path(__file__).parent.joinpath(
        "output_data/bia-study-metadata.json"
    )
    outfile = tmp_path.joinpath("bia-dataset-metadata.json").resolve()

    result = runner.invoke(
        app,
        [
            "website",
            "study",
            "S-BIADTEST",
            "-o",
            outfile,
        ],
    )

    assert result.exit_code == 0

    with open(outfile, "r") as f:
        json_result = json.load(f)

    with open(expected_output) as f:
        json_expected = json.load(f)

    assert json_result == json_expected


# Note that pytest fixture data_in_api is unused in test code,
# but requested in order to guarentee that data is in the test api before running the test
def test_cli_export_website_images(tmp_path: Path, data_in_api):
    expected_output = Path(__file__).parent.joinpath(
        "output_data/bia-image-metadata.json"
    )
    outfile = tmp_path.joinpath("bia-image-metadata.json").resolve()

    result = runner.invoke(app, ["website", "image", "S-BIADTEST", "-o", outfile])

    assert result.exit_code == 0

    with open(outfile, "r") as f:
        json_result = json.load(f)

    with open(expected_output) as f:
        json_expected = json.load(f)

    assert json_result == json_expected


# Note that pytest fixture data_in_api is unused in test code,
# but requested in order to guarentee that data is in the test api before running the test
def test_cli_export_dataset_for_website_images(tmp_path: Path, data_in_api):
    expected_output = Path(__file__).parent.joinpath(
        "output_data/bia-dataset-metadata-for-images.json"
    )
    outfile = tmp_path.joinpath("bia-dataset-metadata.json").resolve()

    result = runner.invoke(
        app,
        ["website", "image-dataset", "S-BIADTEST", "-o", outfile],
    )

    assert result.exit_code == 0

    with open(outfile, "r") as f:
        json_result = json.load(f)

    with open(expected_output) as f:
        json_expected = json.load(f)

    assert json_result == json_expected



def test_cli_export_study_ordering(tmp_path: Path, api_studies_in_expected_order: list[dict]):
    outfile = tmp_path.joinpath("bia-dataset-metadata.json").resolve()

    result = runner.invoke(
        app,
        [
            "website",
            "study",
            "-o",
            outfile,
        ],
    )

    assert result.exit_code == 0

    expected_study_acc_id_order = [study["accession_id"] for study in api_studies_in_expected_order]

    with open(outfile, "r") as f:
        json_result: dict = json.load(f)

    it = iter(json_result.keys()) 
    assert all(acc_id in it for acc_id in expected_study_acc_id_order)