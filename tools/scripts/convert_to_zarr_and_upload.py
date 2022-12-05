import os
import logging
import subprocess
from pathlib import Path

import click
import shutil
import requests
from pydantic import BaseSettings


from bia_integrator_tools.io import c2zsettings, copy_local_to_s3
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.interface import persist_image_representation


logger = logging.getLogger(__file__)


BIOFORMATS2RAW_JAVA_HOME = os.environ["BIOFORMATS2RAW_JAVA_HOME"]
BIOFORMATS2RAW_BIN = os.environ["BIOFORMATS2RAW_BIN"]


def upload_multiple_files_to_s3(src_dst_list):
    """Upload multiple files to S3, expected input is a list of:
    (source file local path, destination key) tuples.
    Credentials, endpoint and bucket assumed to be determined by global config."""

    for src_fpath, dst_key in src_dst_list:
        copy_local_to_s3(src_fpath, dst_key)


def get_s3_key_prefix(accession_id, image_id):

    return f"{accession_id}/{image_id}"


def copy_uri_to_local(src_uri: str, dst_fpath: Path):
    """Copy the object at the given source URI to the local path specified by dst_fpath."""

    logger.info(f"Fetching {src_uri} to {dst_fpath}")

    with requests.get(src_uri, stream=True) as r:
        with open(dst_fpath, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)

            
def run_zarr_conversion(input_fpath, output_dirpath):
    """Convert the local file at input_fpath to Zarr format, in a directory specified by
    output_dirpath"""

    zarr_cmd = f'export JAVA_HOME={BIOFORMATS2RAW_JAVA_HOME} && {BIOFORMATS2RAW_BIN} "{input_fpath}" "{output_dirpath}"'

    logger.info(f"Converting with {zarr_cmd}")
    retval = subprocess.run(zarr_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert retval.returncode == 0, f"Error converting to zarr: {retval.stderr.decode('utf-8')}"

    
def copy_local_zarr_to_s3(zarr_fpath: Path, accession_id: str, image_id: str) -> str:
    """Copy the zarr at the given local path to S3, credentials, bucket and endpoint will
    be taken from global config. Return the URI of the Zarr generated."""

    endpoint_url = c2zsettings.endpoint_url
    bucket_name = c2zsettings.bucket_name

    zarr_parent_dirpath = zarr_fpath.parent

    s3_key_prefix = get_s3_key_prefix(accession_id, image_id)

    upload_list = []
    for f in zarr_fpath.rglob("*"):
        if f.is_file():
            upload_list.append((f, f"{s3_key_prefix}/{f.relative_to(zarr_parent_dirpath)}"))

    upload_multiple_files_to_s3(upload_list)

    zarr_image_uri = f"{endpoint_url}/{bucket_name}/{s3_key_prefix}/{image_id}.zarr/0"

    return zarr_image_uri


@click.command()
@click.argument("accession_id")
@click.argument("image_id")
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    image = bia_study.images[image_id]

    dst_dir_basepath = Path("tmp/c2z")/accession_id
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)

    image_suffix = image.original_relpath.suffix
    dst_fpath = dst_dir_basepath/f"{image_id}{image_suffix}"

    # FIXME - this should check for the correct representation type, not assume it's the first one
    src_uri = image.representations[0].uri
    if not dst_fpath.exists():
        copy_uri_to_local(src_uri, dst_fpath)

    zarr_fpath = dst_dir_basepath/f"{image_id}.zarr"
    if not zarr_fpath.exists():
        run_zarr_conversion(dst_fpath, zarr_fpath)

    zarr_image_uri = copy_local_zarr_to_s3(zarr_fpath, accession_id, image_id)

    representation = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=0,
        type="ome_ngff",
        uri=zarr_image_uri,
        dimensions=None
    )

    persist_image_representation(representation)
        



if __name__ == "__main__":
    main()