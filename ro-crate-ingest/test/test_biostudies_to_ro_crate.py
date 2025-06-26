from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest
import pytest

runner = CliRunner()


@pytest.mark.parametrize(
    "accession_id", ["S-BIAD1494", "S-BIAD843", "S-BIAD1556", "S-BIAD1932"]
)
def test_biostudies_to_ro_crate(accession_id: str, tmp_bia_data_dir: Path):

    result = runner.invoke(
        ro_crate_ingest, ["biostudies-to-roc", "-c", tmp_bia_data_dir, accession_id]
    )

    assert result.exit_code == 0
