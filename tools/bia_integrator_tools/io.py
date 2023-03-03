from pathlib import Path
import logging
import shutil
from urllib.parse import urlparse

import boto3
import requests
from pydantic import BaseSettings
from bia_integrator_core.models import FileReference

    
logger = logging.getLogger(__name__)


class C2ZSettings(BaseSettings):
    endpoint_url: str = "https://uk1s3.embassy.ebi.ac.uk"
    bucket_name: str = "bia-integrator-data"


c2zsettings = C2ZSettings()


def copy_uri_to_local(src_uri: str, dst_fpath: Path):
    """Copy the object at the given source URI to the local path specified by dst_fpath."""

    logger.info(f"Fetching {src_uri} to {dst_fpath}")

    with requests.get(src_uri, stream=True) as r:
        with open(dst_fpath, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)


def put_string_to_s3(string: str, dst_key: str) -> str:
    """Put the given string to the given key."""

    endpoint_url = c2zsettings.endpoint_url
    bucket_name = c2zsettings.bucket_name

    s3 = boto3.resource('s3', endpoint_url=endpoint_url)
    logger.info(f"Uploading {string} to {dst_key}")
    s3.Object(bucket_name, dst_key).put(Body=string, ACL="public-read")
  
    return f"{endpoint_url}/{bucket_name}/{dst_key}"


def copy_local_to_s3(src_fpath: Path, dst_key: str) -> str:
    """Copy the local file with the given path to the S3 location for which the endpoint
    and bucket are described in the global Config object, and the destination key is
    passed as an argument.
    
    Returns: URI of uploaded object."""

    endpoint_url = c2zsettings.endpoint_url
    bucket_name = c2zsettings.bucket_name

    s3 = boto3.resource('s3', endpoint_url=endpoint_url)
    logger.info(f"Uploading {src_fpath} to {dst_key}")
    response = s3.meta.client.upload_file(str(src_fpath), bucket_name, dst_key, ExtraArgs = {"ACL": "public-read"}) # type: ignore

    return f"{endpoint_url}/{bucket_name}/{dst_key}"


def upload_multiple_files_to_s3(src_dst_list):
    """Upload multiple files to S3, expected input is a list of:
    (source file local path, destination key) tuples.
    Credentials, endpoint and bucket assumed to be determined by global config."""

    for src_fpath, dst_key in src_dst_list:
        copy_local_to_s3(src_fpath, dst_key)


def get_s3_key_prefix(accession_id, image_id):

    return f"{accession_id}/{image_id}"


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


def stage_fileref_and_get_fpath(accession_id: str, fileref: FileReference) -> Path:

    cache_root_dirpath = Path.home()/".cache"/"bia-converter"
    cache_dirpath = cache_root_dirpath/accession_id
    cache_dirpath.mkdir(exist_ok=True, parents=True)

    suffix = Path(urlparse(fileref.uri).path).suffix
    dst_fname = fileref.id+suffix
    dst_fpath = cache_dirpath/dst_fname
    logger.info(f"Checking cache for {fileref.name}")

    if not dst_fpath.exists():
        copy_uri_to_local(fileref.uri, dst_fpath)
        logger.info(f"Downloading file to {dst_fpath}")
    else:
        logger.info(f"File exists at {dst_fpath}")

    return dst_fpath