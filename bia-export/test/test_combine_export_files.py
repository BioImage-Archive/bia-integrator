import json
from pathlib import Path
from typer.testing import CliRunner
import pytest
import sys

sys.path.insert(0, f"{Path(__file__).parent.parent / 'scripts'}")
from scripts.combine_export_files import app


@pytest.fixture
def output_dir_base(tmpdir):
    return Path(tmpdir)


@pytest.fixture
def output_file_bases():
    return ["bia-study-metadata", "bia-dataset-metadata", "bia-image-export"]


@pytest.fixture
def accession_ids():
    return [f"S-BIADTEST{i}" for i in [3, 2, 1, 0]]


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
            value = {"release_date": f"{accession_id}:{output_file_base}"}
            output = {
                accession_id: value,
            }
            # Write dummy dict with key "release_date" (needed for sorting studies)
            expected_results[output_file_base][accession_id] = value

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
def test_script_to_combine_export_files_handles_missing_metadata(
    output_dir_base,
    output_file_bases,
    all_expected_results,
    manifest_path,
    metadata_keys_to_exclude,
    accession_id_to_exclude,
):
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


def test_script_to_combine_export_sorts_study_metadata(
    output_dir_base,
    output_file_bases,
    all_expected_results,
    accession_ids,
):
    # Create a manifest file in wrong order and test combined results
    # of study are ordered as expected
    manifest_reversed_path = output_dir_base / "manifest_reversed.txt"
    accession_ids_reversed = [a for a in accession_ids]
    accession_ids_reversed.reverse()
    manifest_reversed_path.write_text(
        "\n".join([f":{a}" for a in accession_ids_reversed])
    )

    runner = CliRunner()
    result = runner.invoke(
        app,
        [
            "combine-export-files",
            f"{manifest_reversed_path}",
        ],
    )
    assert result.exit_code == 0
    for output_file_base in output_file_bases:
        output_path = output_dir_base / f"{output_file_base}.json"
        assert output_path.is_file()
        actual_result = json.loads(output_path.read_text())
        assert all_expected_results[output_file_base] == actual_result
        if output_file_base == "bia-study-metadata":
            assert list(all_expected_results[output_file_base].keys()) == list(
                actual_result.keys()
            )
            assert list(all_expected_results[output_file_base].values()) == list(
                actual_result.values()
            )
        else:
            # dataset and image metadata should not be sorted
            assert list(all_expected_results[output_file_base].keys()) != list(
                actual_result.keys()
            )
            assert list(all_expected_results[output_file_base].values()) != list(
                actual_result.values()
            )
