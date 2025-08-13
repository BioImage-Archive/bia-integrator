from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest
import json
import pytest

runner = CliRunner()


def get_mock_ro_crate_path(accession_id) -> Path:
    return (
        Path(__file__).parents[2]
        / "bia-shared-datamodels"
        / "src"
        / "bia_shared_datamodels"
        / "mock_ro_crate"
        / accession_id
    )


def get_biostudies_to_ro_crate_path(accession_id) -> Path:
    return (
        Path(__file__).parent / "biostudies_to_ro_crate" / "output_data" / accession_id
    )


def get_empiar_to_ro_crate_path(accession_id) -> Path:
    return Path(__file__).parent / "empiar_to_ro_crate" / "output_data" / accession_id


def get_expected_files(accession_id) -> list[Path]:
    expected_out_dir = Path(__file__).parent / "ro_crate_to_bia" / "output_data"

    expected_files = [f for f in expected_out_dir.rglob(f"*/{accession_id}/*.json")]

    return expected_files


@pytest.mark.parametrize(
    "accession_id", ["S-BIAD1494", "S-BIAD843", "S-BIADWITHFILELIST"]
)
def test_ingest_mock_ro_crate_metadata(accession_id: str, tmp_bia_data_dir: Path):

    crate_path = get_mock_ro_crate_path(accession_id)

    ingest_local_test(accession_id, tmp_bia_data_dir, crate_path)


@pytest.mark.parametrize(
    "accession_id", ["S-BIAD1494", "S-BIAD843", "S-BIADWITHFILELIST"]
)
def test_ingest_mock_ro_crate_metadata_with_api(accession_id: str, get_bia_api_client):

    crate_path = get_mock_ro_crate_path(accession_id)

    ingest_api_test(accession_id, get_bia_api_client, crate_path)


@pytest.mark.parametrize(
    "accession_id", ["S-BIADTEST_AUTHOR_AFFILIATION", "S-BIADTEST_COMPLEX_BIOSAMPLE", "S-BIADTEST_PROTOCOL_STUDY"]
)
def test_ingest_biostudies_ro_crate_metadata(accession_id: str, tmp_bia_data_dir: Path):

    crate_path = get_biostudies_to_ro_crate_path(accession_id)

    ingest_local_test(
        accession_id, tmp_bia_data_dir, crate_path, file_ref_url_prefix="biostudies"
    )


@pytest.mark.parametrize(
    "accession_id", ["S-BIADTEST_AUTHOR_AFFILIATION", "S-BIADTEST_COMPLEX_BIOSAMPLE", "S-BIADTEST_PROTOCOL_STUDY"]
)
def test_ingest_biostudies_ro_crate_metadata_with_api(
    accession_id: str, get_bia_api_client
):

    crate_path = get_biostudies_to_ro_crate_path(accession_id)

    ingest_api_test(
        accession_id, get_bia_api_client, crate_path, file_ref_url_prefix="biostudies"
    )


@pytest.mark.parametrize("accession_id", ["EMPIAR-ANNOTATIONTEST"])
def test_ingest_empiar_ro_crate_metadata(accession_id: str, tmp_bia_data_dir: Path):

    crate_path = get_empiar_to_ro_crate_path(accession_id)

    ingest_local_test(
        accession_id, tmp_bia_data_dir, crate_path, file_ref_url_prefix="empiar"
    )


@pytest.mark.parametrize("accession_id", ["EMPIAR-ANNOTATIONTEST"])
def test_ingest_empiar_ro_crate_metadata_with_api(
    accession_id: str, get_bia_api_client
):

    crate_path = get_empiar_to_ro_crate_path(accession_id)

    ingest_api_test(
        accession_id, get_bia_api_client, crate_path, file_ref_url_prefix="empiar"
    )


def ingest_local_test(
    accession_id: str,
    tmp_bia_data_dir: Path,
    crate_path: Path,
    file_ref_url_prefix: str = None,
):

    arguments = ["ingest", "-c", crate_path]
    if file_ref_url_prefix:
        arguments.extend(["-u", file_ref_url_prefix])
    result = runner.invoke(ro_crate_ingest, arguments)

    assert result.exit_code == 0

    files_written = [f for f in tmp_bia_data_dir.rglob(f"*/{accession_id}/*.json")]

    expected_files = get_expected_files(accession_id)

    assert len(files_written) == len(expected_files)

    for file in expected_files:
        relative_file_path = Path(file).parts[-3:]
        expected_path_of_written_file = tmp_bia_data_dir / Path(*relative_file_path)

        assert expected_path_of_written_file.exists()

        with open(expected_path_of_written_file, "r") as f:
            cli_out = json.load(f)

        with open(file, "r") as f:
            expected_out = json.load(f)

        assert cli_out == expected_out


def ingest_api_test(
    accession_id: str,
    get_bia_api_client,
    crate_path: Path,
    file_ref_url_prefix: str = None,
):
    arguments = ["ingest", "-c", crate_path, "-p", "local_api"]
    if file_ref_url_prefix:
        arguments.extend(["-u", file_ref_url_prefix])
    result = runner.invoke(ro_crate_ingest, arguments)

    assert result.exit_code == 0

    expected_files = get_expected_files(accession_id)

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
