from pathlib import Path
import logging
import shutil

import boto3
import requests
from pydantic import BaseSettings

    
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