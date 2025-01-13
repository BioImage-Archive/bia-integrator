from typer.testing import CliRunner
from pathlib import Path
from bia_export.cli import app
import json

runner = CliRunner()


def test_cli_export_website_studies_api(tmp_path: Path, docker_api):
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
