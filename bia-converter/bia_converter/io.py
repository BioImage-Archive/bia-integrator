from pathlib import Path
import logging
import shutil
import subprocess
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import settings


logger = logging.getLogger(__name__)


def sync_dirpath_to_s3(src_dirpath, dst_suffix):
    bucket_name = settings.bucket_name
    logger.info(f"Uploading to bucket {bucket_name} with suffix {dst_suffix}")

    dst_key = f"{bucket_name}/{dst_suffix}"

    cmd = f'aws --region us-east-1 --endpoint-url {settings.endpoint_url} s3 sync "{src_dirpath}/" s3://{dst_key} --acl public-read'
    logger.info(f"Uploading using command {cmd}")

    subprocess.run(cmd, shell=True)

    uri = f"{settings.endpoint_url}/{dst_key}"

    return uri


def upload_dirpath_as_zarr_image_rep(src_dirpath, accession_id, image_id, image_rep_id):
    dst_prefix = (
        f"{settings.bucket_name}/{accession_id}/{image_id}/{image_rep_id}.ome.zarr"
    )
    logger.info(f"Uploading with prefix {dst_prefix}")
    cmd = f'aws --region us-east-1 --endpoint-url {settings.endpoint_url} s3 sync "{src_dirpath}/" s3://{dst_prefix} --acl public-read'
    logger.info(f"Uploading using command {cmd}")
    subprocess.run(cmd, shell=True)

    uri = f"{settings.endpoint_url}/{dst_prefix}"

    return uri


def copy_uri_to_local(src_uri: str, dst_fpath: Path):
    """Copy the object at the given source URI to the local path specified by dst_fpath."""

    logger.info(f"Fetching {src_uri} to {dst_fpath}")

    # Create session with retry strategy
    session = requests.Session()
    retries = Retry(
        total=3,  # number of retries
        backoff_factor=0.3,  # delay factor between retries # type: ignore
        status_forcelist=[500, 502, 503, 504],  # HTTP status codes to retry
        allowed_methods=frozenset({"GET", "HEAD", "OPTIONS"}),
    )
    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    # Ensure parent directory exists
    dst_fpath.parent.mkdir(parents=True, exist_ok=True)

    # Use a temporary file for downloading
    temp_file = dst_fpath.with_suffix(dst_fpath.suffix + ".tmp")

    try:
        with session.get(src_uri, stream=True) as r:
            r.raise_for_status()
            with open(temp_file, "wb") as fh:
                shutil.copyfileobj(r.raw, fh)  # type: ignore

        # If download completed successfully, rename temp file
        temp_file.rename(dst_fpath)

    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download {src_uri}: {str(e)}")
        if temp_file.exists():
            temp_file.unlink()
        raise

    finally:
        session.close()
        if temp_file.exists():
            temp_file.unlink()


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


def encode_url(url):
    # Split into base and path components to preserve the ://
    if "://" in url:
        base, path = url.split("://", 1)
        # Encode the path portion, preserving forward slashes
        encoded_path = quote(path, safe="/")
        return f"{base}://{encoded_path}"
    else:
        # If no protocol specified, encode the whole string
        return quote(url)


def fetch_fileref_to_local(fileref, dst_fpath, max_retries=3):
    # if fileref.type == "file_in_zip":
    #     raise NotImplementedError
    # else:
    # Check size after download and retry if necessary

    encoded_uri = encode_url(fileref.uri)
    expected_size = (
        requests.header(encoded_uri)["content-length"]
        if fileref.size_in_bytes == 0
        else fileref.size_in_bytes
    )  # type: ignore
    for attempt in range(1, max_retries + 1):
        try:
            copy_uri_to_local(encoded_uri, dst_fpath)
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

    suffix = Path(fileref.file_path).suffix
    dst_fname = fileref.uuid + suffix
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


# type: ignore
