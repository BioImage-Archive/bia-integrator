# All code in this module originate from bia-converter/bia_converter/io.py

from typing import List
from bia_shared_datamodel import bia_data_model
import logging
import subprocess


from ..config import settings

logger = logging.getLogger(__name__)


def run_zarr_conversion(input_fpath, output_dirpath):
    """Convert the local file at input_fpath to Zarr format, in a directory specified by
    output_dirpath"""

    zarr_cmd = f'export JAVA_HOME={settings.bioformats2raw_java_home} && {settings.bioformats2raw_bin} "{input_fpath}" "{output_dirpath}"'

    logger.info(f"Converting with {zarr_cmd}")

    retval = subprocess.run(
        zarr_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert (
        retval.returncode == 0
    ), f"Error converting to zarr: {retval.stderr.decode('utf-8')}"


def cached_convert_to_zarr_and_get_fpath(image, input_fpath):
    dst_dir_basepath = settings.cache_root_dirpath / "zarr"
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)

    zarr_fpath = dst_dir_basepath / f"{image.uuid}.zarr"
    if not zarr_fpath.exists():
        run_zarr_conversion(input_fpath, zarr_fpath)

    return zarr_fpath


def convert_to_zarr(
    file_references: List[bia_data_model.FileReference],
    zarr_location: str,
    overwrite: bool = False,
) -> None:
    """Convert the given file reference to a zarr at given location downloading if necessary"""
