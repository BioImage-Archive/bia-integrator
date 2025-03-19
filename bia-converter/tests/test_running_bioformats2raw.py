"""Test running bioformats2raw with singularity and docker"""

from pathlib import Path
import filecmp
import shutil
import pytest

from bia_converter.conversion import (
    run_bioformats2raw_with_singularity,
    run_bioformats2raw_with_docker,
)

singularity_not_available = shutil.which("singularity") is None


@pytest.fixture
def file_to_convert() -> Path:
    return Path(__file__).parent / "data" / "im06.png"


@pytest.fixture
def path_to_expected_output() -> Path:
    return Path(__file__).parent / "data" / "im06.ome.zarr"


@pytest.fixture(scope="function")
def output_dirpath(tmp_path) -> Path:
    """Return path to which converted zarr should be saved"""

    return tmp_path / "converted.zarr"


def test_run_bioformats2raw_with_docker(
    file_to_convert, output_dirpath, path_to_expected_output
):
    run_bioformats2raw_with_docker(file_to_convert, output_dirpath)

    comparison = filecmp.dircmp(output_dirpath, path_to_expected_output)
    assert not comparison.left_only
    assert not comparison.right_only
    assert not comparison.diff_files


@pytest.mark.skipif(singularity_not_available, reason="Singularity is not installed")
def test_run_bioformats2raw_with_singularity(
    file_to_convert, output_dirpath, path_to_expected_output
):
    run_bioformats2raw_with_singularity(file_to_convert, output_dirpath)

    comparison = filecmp.dircmp(output_dirpath, path_to_expected_output)
    assert not comparison.left_only
    assert not comparison.right_only
    assert not comparison.diff_files
