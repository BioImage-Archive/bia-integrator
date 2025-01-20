from typer.testing import CliRunner
from pathlib import Path
from bia_export.cli import app
import json

runner = CliRunner()


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
        "output_data/bia-image-export.json"
    )
    outfile = tmp_path.joinpath("bia-image-export.json").resolve()

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
