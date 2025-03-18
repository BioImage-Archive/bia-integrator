"""Test running bioformats2raw with singularity and docker"""

from pathlib import Path
import filecmp
import pytest

from bia_converter.conversion import (
    run_bioformats2raw_with_singularity,
    run_bioformats2raw_with_docker,
)


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


@pytest.mark.parametrize(
    "bioformats2raw_function",
    (run_bioformats2raw_with_docker, run_bioformats2raw_with_singularity),
)
def test_run_bioformats2raw_with_docker(
    bioformats2raw_function, file_to_convert, output_dirpath, path_to_expected_output
):
    bioformats2raw_function(file_to_convert, output_dirpath)

    comparison = filecmp.dircmp(output_dirpath, path_to_expected_output)
    assert not comparison.left_only
    assert not comparison.right_only
    assert not comparison.diff_files
