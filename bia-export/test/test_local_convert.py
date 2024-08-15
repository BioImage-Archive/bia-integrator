from typer.testing import CliRunner
from pathlib import Path
import pytest
from bia_export.cli import app
import filecmp

runner = CliRunner()



def test_cli_export_website_studies(tmp_path: Path):
    input_root_path = Path(__file__).parent.joinpath("input_data")
    expected_output = Path(__file__).parent.joinpath("output_data/bia_export.json")
    outfile = tmp_path.joinpath('bia_export.json').resolve()

    result = runner.invoke(app, ["website-study", "S-BIADTEST", "-o", outfile, "-r", input_root_path])



    assert result.exit_code == 0
    # Note this tests for exact equivance in files, i.e. order of fields and indentation matters
    assert filecmp.cmp(expected_output, outfile, shallow=False)



def test_cli_export_website_images(tmp_path: Path):
    input_root_path = Path(__file__).parent.joinpath("input_data")
    expected_output = Path(__file__).parent.joinpath("output_data/bia_image_export.json")
    outfile = tmp_path.joinpath('bia_image_export.json').resolve()

    result = runner.invoke(app, ["website-image", "S-BIADTEST", "-o", outfile, "-r", input_root_path])


    assert result.exit_code == 0
    # Note this tests for exact equivance in files, i.e. order of fields and indentation matters
    assert filecmp.cmp(expected_output, outfile, shallow=False)
