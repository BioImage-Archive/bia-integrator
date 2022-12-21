import logging
import subprocess

from pydantic import BaseSettings

class ConversionSettings(BaseSettings):
    bioformats2raw_java_home: str
    bioformats2raw_bin: str

    class Config:
        env_file = '.env'


logger = logging.getLogger(__name__)


settings = ConversionSettings()


def run_zarr_conversion(input_fpath, output_dirpath):
    """Convert the local file at input_fpath to Zarr format, in a directory specified by
    output_dirpath"""

    zarr_cmd = f'export JAVA_HOME={settings.bioformats2raw_java_home} && {settings.bioformats2raw_bin} "{input_fpath}" "{output_dirpath}"'

    logger.info(f"Converting with {zarr_cmd}")
    retval = subprocess.run(zarr_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert retval.returncode == 0, f"Error converting to zarr: {retval.stderr.decode('utf-8')}"
