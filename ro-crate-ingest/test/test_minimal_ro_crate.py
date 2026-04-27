from pathlib import Path
from typer.testing import CliRunner
from ro_crate_ingest.cli import ro_crate_ingest
from ro_crate_ingest.empiar_to_ro_crate.entity_conversion.file_list import (
    expand_dataframe_metadata,
)
import pytest
from .conftest import (
    expected_path_to_created_path,
    get_expected_ro_crate_directory,
    get_created_ro_crate_metadata,
    get_expected_ro_crate_metadata,
)
import glob
import pandas as pd
import logging

runner = CliRunner()


@pytest.mark.parametrize(
    "accession_id",
    ["EMPIAR-IMAGEPATTERNTEST"],
)
def test_minimal_ro_crate(accession_id: str, tmp_bia_data_dir: Path):

    result = runner.invoke(
        ro_crate_ingest, ["minimal-roc", accession_id, "-c", tmp_bia_data_dir]
    )
    assert result.exit_code == 0

    expected_metadata = get_expected_ro_crate_metadata(
        accession_id, "minimal_ro_crate"
    )
    created_ro_crate_metadata = get_created_ro_crate_metadata(
        tmp_bia_data_dir, accession_id
    )
    assert created_ro_crate_metadata["@context"] == expected_metadata["@context"]
    assert sorted(
        created_ro_crate_metadata["@graph"], key=lambda d: d["@id"]
    ) == sorted(expected_metadata["@graph"], key=lambda d: d["@id"])

    expected_files = glob.glob(
        f"{get_expected_ro_crate_directory(accession_id, 'minimal_ro_crate')}/**/*",
        recursive=True,
    )
    created_files = glob.glob(f"{tmp_bia_data_dir / accession_id}/**/*", recursive=True)

    assert len(expected_files) == len(created_files)
    for expected_file in expected_files:
        if expected_file.endswith(".tsv"):
            created_file_path = expected_path_to_created_path(
                expected_file, tmp_bia_data_dir, "minimal_ro_crate"
            )
            expected_tsv = pd.read_csv(expected_file, sep="\t")
            created_tsv = pd.read_csv(created_file_path, sep="\t")
            pd.testing.assert_frame_equal(expected_tsv, created_tsv)

    validation_result = runner.invoke(
        ro_crate_ingest, ["validate", str(tmp_bia_data_dir / accession_id)]
    )
    assert validation_result.exit_code == 0


def test_expand_dataframe_metadata_can_skip_premature_unassigned_debug(caplog):
    file_df = pd.DataFrame(
        [
            {
                "file_path": Path("data/raw_data/eer/TIR520_029_22.00_20230406_101156_EER.eer"),
                "size_in_bytes": 123,
            }
        ]
    )

    with caplog.at_level(
        logging.DEBUG, logger="__main__.ro_crate_ingest.empiar_to_ro_crate.entity_conversion.file_list"
    ):
        expand_dataframe_metadata([], file_df, report_unassigned=False)

    assert "Unassigned file detected" not in caplog.text
