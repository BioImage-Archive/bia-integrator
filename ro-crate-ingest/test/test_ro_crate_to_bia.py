from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest
import json
from bia_integrator_api import models
from pydantic.alias_generators import to_pascal

runner = CliRunner()


def test_ingest_ro_crate_metadata(tmp_bia_data_dir: Path):

    test_study_accession_id = "S-BIAD1494"

    crate_path = (
        Path(__file__).parents[2]
        / "bia-shared-datamodels"
        / "src"
        / "bia_shared_datamodels"
        / "mock_ro_crate"
        / test_study_accession_id
    )

    result = runner.invoke(ro_crate_ingest, ["-c", crate_path])

    assert result.exit_code == 0

    files_written = [
        f for f in tmp_bia_data_dir.rglob(f"*/{test_study_accession_id}/*.json")
    ]

    expected_out_dir = Path(__file__).parent / "ro_crate_to_bia" / "output_data"

    expected_files = [
        f for f in expected_out_dir.rglob(f"*/{test_study_accession_id}/*.json")
    ]

    assert len(files_written) == len(expected_files)

    for file in expected_files:
        relative_file_path = Path(file).parts[-3:]
        expected_path_of_written_file = expected_out_dir / Path(*relative_file_path)

        assert expected_path_of_written_file.exists()

        with open(expected_path_of_written_file, "r") as f:
            cli_out = json.load(f)

        with open(file, "r") as f:
            expected_out = json.load(f)

        assert cli_out == expected_out


def test_ingest_ro_crate_metadata_with_api(get_bia_api_client):

    test_study_accession_id = "S-BIAD1494"

    crate_path = (
        Path(__file__).parents[2]
        / "bia-shared-datamodels"
        / "src"
        / "bia_shared_datamodels"
        / "mock_ro_crate"
        / "S-BIAD1494"
    )

    result = runner.invoke(ro_crate_ingest, ["-c", crate_path, "-p", "local_api"])

    assert result.exit_code == 0

    expected_out_dir = Path(__file__).parent / "ro_crate_to_bia" / "output_data"

    expected_files = [
        f for f in expected_out_dir.rglob(f"*/{test_study_accession_id}/*.json")
    ]

    for file in expected_files:
        relative_file_path = Path(file).parts[-3:]

        with open(file, "r") as f:
            expected_out = json.load(f)

        expected_type = relative_file_path[0]
        expected_uuid = expected_out["uuid"]

        api_get_method = f"get_{expected_type}"
        api_obj = getattr(get_bia_api_client, api_get_method)(str(expected_uuid))

        api_obj_type = api_obj.__class__
        expected_object = api_obj_type.model_validate(expected_out)

        assert api_obj == expected_object
