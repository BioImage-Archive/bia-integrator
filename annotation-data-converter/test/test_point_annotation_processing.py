from typer.testing import CliRunner
from annotation_data_converter.cli import annotation_data_convert

runner = CliRunner()


def test_nlr_starfile_convert(data_in_api):

    commands = [
        "-ad",
        "d66a17df-a878-44f0-b10b-f6f773896924",
        "-ir",
        "520e7b09-33f6-4351-8622-0dedaf8a4f4e",
        "-p",
        "../ro-crate-ingest/proposals/empiar_11058.yaml",
        "-pm",
        "rln",
        "-am",
        "local_api",
    ]

    result = runner.invoke(annotation_data_convert, commands)
    assert result.exit_code == 1
