from typer.testing import CliRunner
from pathlib import Path
from bia_export.cli import app
import json

runner = CliRunner()


def test_cli_export_website_studies(tmp_path: Path):
    input_root_path = Path(__file__).parent.joinpath("input_data")
    expected_output = Path(__file__).parent.joinpath(
        "output_data/bia-study-metadata.json"
    )
    outfile = tmp_path.joinpath("bia-study-metadata.json").resolve()

    result = runner.invoke(
        app, ["website", "study", "S-BIADTEST", "-o", outfile, "-r", input_root_path]
    )

    assert result.exit_code == 0

    with open(outfile, "r") as f:
        json_result = json.load(f)

    with open(expected_output) as f:
        json_expected = json.load(f)

    assert json_result == json_expected


def test_cli_export_website_images(tmp_path: Path):
    input_root_path = Path(__file__).parent.joinpath("input_data")
    expected_output = Path(__file__).parent.joinpath(
        "output_data/bia-image-export.json"
    )
    outfile = tmp_path.joinpath("bia-image-export.json").resolve()

    result = runner.invoke(
        app, ["website", "image", "S-BIADTEST", "-o", outfile, "-r", input_root_path]
    )

    assert result.exit_code == 0

    with open(outfile, "r") as f:
        json_result = json.load(f)

    with open(expected_output) as f:
        json_expected = json.load(f)

    assert json_result == json_expected


def test_cli_export_dataset_for_website_images(tmp_path: Path):
    input_root_path = Path(__file__).parent.joinpath("input_data")
    expected_output = Path(__file__).parent.joinpath(
        "output_data/bia-dataset-metadata-for-images.json"
    )
    outfile = tmp_path.joinpath("bia-dataset-metadata.json").resolve()

    result = runner.invoke(
        app,
        [
            "website",
            "image-dataset",
            "S-BIADTEST",
            "-o",
            outfile,
            "-r",
            input_root_path,
        ],
    )

    assert result.exit_code == 0

    with open(outfile, "r") as f:
        json_result = json.load(f)

    with open(expected_output) as f:
        json_expected = json.load(f)

    assert json_result == json_expected
