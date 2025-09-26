import pytest
import json

from deepdiff import DeepDiff
from pathlib import Path
from typer.testing import CliRunner

from bia_export.cli import app

runner = CliRunner()


@pytest.mark.parametrize(
    "subcommand,expected_file,outfile_name",
    [
        (
            "study",
            "output_data/bia-study-metadata.json",
            "bia-study-metadata.json",
        ),
        (
            "image",
            "output_data/bia-image-metadata.json",
            "bia-image-metadata.json",
        ),
        (
            "image-dataset",
            "output_data/bia-dataset-metadata-for-images.json",
            "bia-dataset-metadata.json",
        ),
    ],
)
def test_cli_export_website(tmp_path: Path, subcommand, expected_file, outfile_name):
    input_root_path = Path(__file__).parent.joinpath("input_data")
    expected_output = Path(__file__).parent.joinpath(expected_file)
    outfile = tmp_path.joinpath(outfile_name).resolve()

    ingest_command = [
        "website",
        subcommand,
        "S-BIADTEST",
        "-o",
        outfile,
        "-r",
        str(input_root_path),
    ]

    result = runner.invoke(app, ingest_command)
    assert result.exit_code == 0

    with open(outfile, "r") as f:
        json_result = json.load(f)
    with open(expected_output, "r") as f:
        json_expected = json.load(f)

    assert DeepDiff(json_result, json_expected) == {}
