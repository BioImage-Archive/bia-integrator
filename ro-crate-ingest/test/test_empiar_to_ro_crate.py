from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest
import pytest
from .conftest import (
    expected_path_to_created_path,
    get_expected_ro_crate_directory,
    get_created_ro_crate_metadata,
    get_expected_ro_crate_metadata,
)
import glob
import pandas as pd

runner = CliRunner()


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
    ["EMPIAR-ANNOTATIONTEST", "EMPIAR-IMAGEPATTERNTEST"],
)
def test_biostudies_to_ro_crate(accession_id: str, tmp_bia_data_dir: Path):

    proposal_file = get_input_proposal_path(accession_id)

    result = runner.invoke(
        ro_crate_ingest, ["empiar-to-roc", str(proposal_file), "-c", tmp_bia_data_dir]
    )

    assert result.exit_code == 0

    expected_metadata = get_expected_ro_crate_metadata(
        accession_id, "empiar_to_ro_crate"
    )
    created_ro_crate_metadata = get_created_ro_crate_metadata(
        tmp_bia_data_dir, accession_id
    )
    assert created_ro_crate_metadata == expected_metadata

    expected_files = glob.glob(
        f"{get_expected_ro_crate_directory(accession_id, "empiar_to_ro_crate")}/**/*",
        recursive=True,
    )
    created_files = glob.glob(f"{tmp_bia_data_dir / accession_id}/**/*", recursive=True)

    assert len(expected_files) == len(created_files)
    for expected_file in expected_files:
        if expected_file.endswith(".tsv"):
            created_file_path = expected_path_to_created_path(
                expected_file, tmp_bia_data_dir, "empiar_to_ro_crate"
            )
            expected_tsv = pd.read_csv(expected_file, sep="\t")
            created_tsv = pd.read_csv(created_file_path, sep="\t")
            assert expected_tsv.equals(created_tsv)
