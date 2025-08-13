from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest
import pytest
import json
import glob
import pandas as pd

runner = CliRunner()


def get_expected_ro_crate_directory(accession_id: str) -> dict:
    return (
        Path(__file__).parent / "biostudies_to_ro_crate" / "output_data" / accession_id
    )


def get_expected_ro_crate_metadata(accession_id: str) -> dict:
    expected_ro_crate_metadata_path = (
        get_expected_ro_crate_directory(accession_id) / "ro-crate-metadata.json"
    )

    with open(expected_ro_crate_metadata_path) as f:
        return json.loads(f.read())


def get_created_ro_crate_metadata(base_path: Path, accession_id: str):
    created_metatadata_path = base_path / accession_id / "ro-crate-metadata.json"

    with open(created_metatadata_path) as f:
        return json.loads(f.read())


def expected_path_to_created_path(expected_path: str, output_dir: Path) -> Path:
    expected_output_base = (
        Path(__file__).parent / "biostudies_to_ro_crate" / "output_data"
    )
    relative = Path(expected_path).relative_to(expected_output_base)
    return output_dir / relative


@pytest.mark.parametrize(
    "accession_id",
    [
        "S-BIADTEST_AUTHOR_AFFILIATION",
        "S-BIADTEST_COMPLEX_BIOSAMPLE",
        "S-BIADTEST_PROTOCOL_STUDY",
    ],
)
def test_biostudies_to_ro_crate(accession_id: str, tmp_bia_data_dir: Path):

    result = runner.invoke(
        ro_crate_ingest, ["biostudies-to-roc", "-c", tmp_bia_data_dir, accession_id]
    )

    assert result.exit_code == 0

    expected_metadata = get_expected_ro_crate_metadata(accession_id)
    created_ro_crate_metadata = get_created_ro_crate_metadata(
        tmp_bia_data_dir, accession_id
    )
    assert created_ro_crate_metadata == expected_metadata

    expected_files = glob.glob(
        f"{get_expected_ro_crate_directory(accession_id)}/**/*", recursive=True
    )
    created_files = glob.glob(f"{tmp_bia_data_dir / accession_id}/**/*", recursive=True)

    assert len(expected_files) == len(created_files)
    for expected_file in expected_files:
        if expected_file.endswith(".tsv"):
            created_file_path = expected_path_to_created_path(
                expected_file, tmp_bia_data_dir
            )
            expected_tsv = pd.read_csv(expected_file, sep="\t")
            created_tsv = pd.read_csv(created_file_path, sep="\t")
            assert expected_tsv.equals(created_tsv)
