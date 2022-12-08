import os
import logging
import subprocess


BIOFORMATS2RAW_JAVA_HOME = os.environ["BIOFORMATS2RAW_JAVA_HOME"]
BIOFORMATS2RAW_BIN = os.environ["BIOFORMATS2RAW_BIN"]


logger = logging.getLogger(__name__)


def run_zarr_conversion(input_fpath, output_dirpath):
    """Convert the local file at input_fpath to Zarr format, in a directory specified by
    output_dirpath"""

    zarr_cmd = f'export JAVA_HOME={BIOFORMATS2RAW_JAVA_HOME} && {BIOFORMATS2RAW_BIN} "{input_fpath}" "{output_dirpath}"'

    logger.info(f"Converting with {zarr_cmd}")
    retval = subprocess.run(zarr_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert retval.returncode == 0, f"Error converting to zarr: {retval.stderr.decode('utf-8')}"
