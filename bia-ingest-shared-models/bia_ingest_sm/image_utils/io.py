# All code in this module originate from bia-converter/bia_converter/io.py

from pathlib import Path
import logging
import shutil
import subprocess

import requests

from ..config import settings
from .image_utils import get_image_extension


logger = logging.getLogger(__name__)


def upload_dirpath_as_zarr_image_rep(src_dirpath, accession_id, image_id):
    dst_prefix = f"{settings.bucket_name}/{accession_id}/{image_id}/{image_id}.zarr"
    logger.info(f"Uploading with prefix {dst_prefix}")
    cmd = f'aws --region us-east-1 --endpoint-url {settings.endpoint_url} s3 sync "{src_dirpath}/" s3://{dst_prefix} --acl public-read'
    logger.info(f"Uploading using command {cmd}")
    subprocess.run(cmd, shell=True)

    uri = f"{settings.endpoint_url}/{settings.bucket_name}/{accession_id}/{image_id}/{image_id}.zarr"

    return uri


def copy_uri_to_local(src_uri: str, dst_fpath: Path):
    """Copy the object at the given source URI to the local path specified by dst_fpath."""

    logger.info(f"Fetching {src_uri} to {dst_fpath}")

    with requests.get(src_uri, stream=True) as r:
        r.raise_for_status()
        with open(dst_fpath, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)


def copy_local_to_s3(src_fpath: Path, dst_key: str) -> str:
    """Copy the local file with the given path to the S3 location for which the endpoint
    and bucket are described in the global Config object, and the destination key is
    passed as an argument.

    Returns: URI of uploaded object."""

    endpoint_url = settings.endpoint_url
    bucket_name = settings.bucket_name

    cmd = f"aws --region us-east-1 --endpoint-url {settings.endpoint_url} s3 cp {src_fpath} s3://{bucket_name}/{dst_key} --acl public-read"
    logger.info(f"Uploading {src_fpath} to {dst_key}")
    subprocess.run(cmd, shell=True)

    return f"{endpoint_url}/{bucket_name}/{dst_key}"


def fetch_fileref_to_local(fileref, dst_fpath, max_retries=3):
    # TODO: Clarify if 'format' represents old 'type' e.g. fire_object, file_in_zip etc.
    # if fileref.type == "file_in_zip":
    if fileref.format == "file_in_zip":
        raise NotImplementedError
    else:
        # Check size after download and retry if necessary
        expected_size = (
            requests.header(fileref.uri)["content-length"]
            if fileref.size_in_bytes == 0
            else fileref.size_in_bytes
        )
        for attempt in range(1, max_retries + 1):
            try:
                copy_uri_to_local(fileref.uri, dst_fpath)
                download_size = dst_fpath.stat().st_size
                if download_size == expected_size:
                    break

                logger.warning(
                    f"Download attempt {attempt} did not give expected size. Got {download_size} expected {expected_size}"
                )
                if attempt >= max_retries:
                    raise Exception(
                        f"{attempt} download attempt(s) did not give expected size. Got {download_size} expected {expected_size}. Maximum retries reached"
                    )
            except requests.exceptions.HTTPError as download_error:
                if attempt >= max_retries:
                    logger.error(
                        f"Download attempt {attempt} resulted in error: {download_error} - exiting"
                    )
                    raise download_error


# ToDo add max_retries as parameter to function definition
def stage_fileref_and_get_fpath(fileref) -> Path:
    cache_dirpath = settings.cache_root_dirpath / "files"
    cache_dirpath.mkdir(exist_ok=True, parents=True)

    # suffix = Path(urlparse(fileref.file_path).path).suffix
    suffix = get_image_extension(fileref.file_path)
    dst_fname = f"{fileref.uuid}{suffix}"
    dst_fpath = cache_dirpath / dst_fname
    logger.info(f"Checking cache for {fileref.file_path}")

    if not dst_fpath.exists():
        logger.info(f"File not in cache. Downloading file to {dst_fpath}")
        fetch_fileref_to_local(fileref, dst_fpath)
    elif dst_fpath.stat().st_size != fileref.size_in_bytes:
        # ToDo: As of 04/12/2023 filerefs for type file_in_zip have size_in_bytes=0
        # Need to modify index_from_zips to get filesize info
        logger.info(
            f"File in cache with size {dst_fpath.stat().st_size}. Expected size={fileref.size_in_bytes}. Downloading again to {dst_fpath}"
        )
        fetch_fileref_to_local(fileref, dst_fpath)
    else:
        logger.info(f"File exists at {dst_fpath}")

    return dst_fpath
