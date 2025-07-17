from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest
import pytest
import json

runner = CliRunner()


def get_expected_ro_crate_metadata(accession_id: str) -> dict:
    expected_ro_crate_metadata_path = (
        Path(__file__).parent
        / "empiar_to_ro_crate"
        / "output_data"
        / accession_id
        / "ro-crate-metadata.json"
    )

    with open(expected_ro_crate_metadata_path) as f:
        return json.loads(f.read())


def get_created_ro_crate_metadata(base_path: Path, accession_id: str) -> dict:
    created_metatadata_path = base_path / accession_id / "ro-crate-metadata.json"

    with open(created_metatadata_path) as f:
        return json.loads(f.read())


def get_input_proposal_path(accession_id: str) -> Path:
    proposal_filename = accession_id.lower().replace("-", "_")
    return (
        Path(__file__).parent
        / "empiar_to_ro_crate"
        / "proposal"
        / f"{proposal_filename}.yaml"
    )


@pytest.mark.parametrize(
    "accession_id",
    ["EMPIAR-TEST"],
)
def test_biostudies_to_ro_crate(accession_id: str, tmp_bia_data_dir: Path):

    proposal_file = get_input_proposal_path(accession_id)

    result = runner.invoke(
        ro_crate_ingest, ["empiar-to-roc", str(proposal_file), "-c", tmp_bia_data_dir]
    )

    assert result.exit_code == 0

    expected_metadata = get_expected_ro_crate_metadata(accession_id)
    created_ro_crate_metadata = get_created_ro_crate_metadata(
        tmp_bia_data_dir, accession_id
    )
    assert created_ro_crate_metadata == expected_metadata
