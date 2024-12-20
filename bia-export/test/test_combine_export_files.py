import json
from pathlib import Path
from typer.testing import CliRunner
import pytest
import sys

sys.path.insert(0, f"{Path(__file__).parent.parent / 'scripts'}")
from scripts.combine_export_files import app


#            # Skip writing output for one of each output type
#            if (accession_id == "S-BIADTEST1" and output_file_base == "bia-images-export") or \
#                (accession_id == "S-BIADTEST3" and output_file_base == "bia-dataset-metadata") or \
#                (accession_id == "S-BIADTEST4" and output_file_base == "bia-study-metadata"):
#                continue
@pytest.fixture
def output_dir_base(tmpdir):
    return Path(tmpdir)


@pytest.fixture
def output_file_bases():
    return ["bia-study-metadata", "bia-dataset-metadata", "bia-image-export"]


@pytest.fixture
def accession_ids():
    return [f"S-BIADTEST{i}" for i in range(3)]


@pytest.fixture
def manifest_path(output_dir_base, accession_ids):
    mpath = output_dir_base / "manifest.txt"
    mpath.write_text("\n".join([f":{a}" for a in accession_ids]))
    return mpath


@pytest.fixture
def all_expected_results(
    output_dir_base,
    output_file_bases,
    accession_ids,
):
    expected_results = {key: {} for key in output_file_bases}
    for accession_id in accession_ids:
        for output_file_base in output_file_bases:
            output = {
                accession_id: output_file_base,
            }
            expected_results[output_file_base][accession_id] = output_file_base

            output_path = output_dir_base / f"{output_file_base}-{accession_id}.json"
            Path(output_path).write_text(json.dumps(output, indent=2))
    return expected_results


@pytest.mark.parametrize(
    (
        "metadata_keys_to_exclude",
        "accession_id_to_exclude",
    ),
    (
        # Test all data written if nothing missing
        (
            [],
            "",
        ),
        # Test no data is written for accession ID if study metadata missing
        (
            [
                "bia-study-metadata",
                "bia-dataset-metadata",
                "bia-image-export",
            ],
            "S-BIADTEST1",
        ),
        # Test no dataset and image written for accession ID if dataset metadata missing
        (
            [
                "bia-dataset-metadata",
                "bia-image-export",
            ],
            "S-BIADTEST0",
        ),
        # Test no image written for accession ID if image metadata missing
        (
            [
                "bia-dataset-metadata",
                "bia-image-export",
            ],
            "S-BIADTEST2",
        ),
    ),
)
def test_script_to_combine_export_files_handles_missing_study(
    output_dir_base,
    output_file_bases,
    accession_ids,
    all_expected_results,
    manifest_path,
    metadata_keys_to_exclude,
    accession_id_to_exclude,
):
    # Remove study file for S-BIADTEST1
    if metadata_keys_to_exclude and accession_id_to_exclude:
        for metadata_key in metadata_keys_to_exclude:
            all_expected_results[metadata_key].pop(accession_id_to_exclude)
        to_unlink = f"{metadata_keys_to_exclude[0]}-{accession_id_to_exclude}.json"
        Path(output_dir_base / to_unlink).unlink()
    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "combine-export-files",
            f"{manifest_path}",
        ],
    )
    assert result.exit_code == 0
    for output_file_base in output_file_bases:
        output_path = output_dir_base / f"{output_file_base}.json"
        assert output_path.is_file()
        actual_result = json.loads(output_path.read_text())
        assert all_expected_results[output_file_base] == actual_result
