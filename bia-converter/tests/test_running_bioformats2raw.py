"""Test running bioformats2raw with singularity and docker"""

from pathlib import Path
import filecmp
import shutil
import platform
import pytest

from bia_converter.conversion import (
    run_bioformats2raw_with_singularity,
    run_bioformats2raw_with_docker,
    run_bioformats2raw_java_cli,
    run_zarr_conversion,
)
from bia_converter.config import settings

# As of 19/03/2025 bioformats2raw docker image only built for linux/amd64.
# Some of our macs are running arm64 -> skip docker tests in these cases.
platform_type = platform.machine().lower()
arm64_platform = "arm64" in platform_type
arm64_platform_message = (
    f"Platform={platform_type}. bioformats2raw docker image only built for linux/amd64"
)

singularity_not_available = shutil.which("singularity") is None

bioformats2raw_java_cli_not_available = (
    settings.bioformats2raw_bin == "" or settings.bioformats2raw_java_home == ""
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


@pytest.mark.skipif(arm64_platform, reason=arm64_platform_message)
def test_run_bioformats2raw_with_docker(
    file_to_convert, output_dirpath, path_to_expected_output
):
    run_bioformats2raw_with_docker(file_to_convert, output_dirpath)

    comparison = filecmp.dircmp(output_dirpath, path_to_expected_output)
    assert not comparison.left_only
    assert not comparison.right_only
    assert not comparison.diff_files


@pytest.mark.skipif(arm64_platform, reason=arm64_platform_message)
@pytest.mark.skipif(singularity_not_available, reason="Singularity is not installed")
def test_run_bioformats2raw_with_singularity(
    file_to_convert, output_dirpath, path_to_expected_output
):
    run_bioformats2raw_with_singularity(file_to_convert, output_dirpath)

    comparison = filecmp.dircmp(output_dirpath, path_to_expected_output)
    assert not comparison.left_only
    assert not comparison.right_only
    assert not comparison.diff_files


@pytest.mark.skipif(
    bioformats2raw_java_cli_not_available, reason="bioformats2raw env vars not set"
)
def test_run_bioformats2raw_java_cli(
    file_to_convert, output_dirpath, path_to_expected_output
):
    run_bioformats2raw_java_cli(file_to_convert, output_dirpath)

    comparison = filecmp.dircmp(output_dirpath, path_to_expected_output)
    assert not comparison.left_only
    assert not comparison.right_only
    assert not comparison.diff_files


def test_generic_zarr_conversion(
    file_to_convert, output_dirpath, path_to_expected_output
):
    run_zarr_conversion(file_to_convert, output_dirpath)

    comparison = filecmp.dircmp(output_dirpath, path_to_expected_output)
    assert not comparison.left_only
    assert not comparison.right_only
    assert not comparison.diff_files
