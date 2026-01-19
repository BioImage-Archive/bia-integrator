import logging
import os
import subprocess
from enum import Enum
from pathlib import Path

from persistence.settings import get_settings

logger = logging.getLogger(__name__)


class S3UploadError(Exception):
    """Raised when an S3 upload fails after all retry attempts."""
    pass


class UploadMode(str, Enum):
    COPY = "copy"
    SYNC = "sync"


def upload_to_s3(
    mode: UploadMode, 
    source_path: Path | str, 
    destination_suffix: str, 
    bucket_name: str | None = None, 
    endpoint_url: str | None = None, 
    dry_run: bool = False
) -> str:
    """
    Common function to handle s3 uploads.
    
    Args:
        mode: UploadMode enum — "copy" for single file, "sync" for directory
        source_path: Path to the source, local file or directory
        destination_suffix: The s3 destination suffix (the part after the bucket)
        bucket_name: Name of the S3 bucket; if None, uses settings value from .env
        endpoint_url: Optional S3 endpoint URL; if None, uses settings value from .env
        dry_run: If True, log actions but don't actually upload
        
    Returns:
        URI of the uploaded content
        
    Raises:
        ValueError: If mode is not "sync" or "copy", or if bucket_name is not provided
        S3UploadError: If upload fails after all retry attempts
    """
    settings = get_settings()
    
    if bucket_name is None:
        bucket_name = settings.s3_bucket_name
        if not bucket_name:
            raise ValueError(
                "No S3 bucket name provided. Either pass bucket_name as an argument "
                "or set S3_BUCKET_NAME in your environment/settings."
            )

    if mode == UploadMode.SYNC:
        s3_cmd = "sync"
        source_path = str(source_path)
        if not source_path.endswith('/'):
            source_path += '/'
    elif mode == UploadMode.COPY:
        s3_cmd = "cp"
    else:
        raise ValueError(f'Invalid upload mode: {mode}; must be "copy" or "sync".')
    
    settings = get_settings()
    
    if endpoint_url is None:
        endpoint_url = settings.s3_endpoint_url

    dst_key = f"{bucket_name}/{destination_suffix}"
    s3_uri = f"{endpoint_url}/{dst_key}"
    
    cmd = (
        f'aws --region us-east-1 --endpoint-url {endpoint_url} '
        f's3 {s3_cmd} "{source_path}" s3://{dst_key} --acl public-read'
    )

    if dry_run:
        logger.info(
            f"Dry run: would upload {source_path} to s3://{dst_key} "
            f"with command: {cmd}"
        )
        return s3_uri
    
    env = os.environ.copy()
    env["AWS_REQUEST_CHECKSUM_CALCULATION"] = settings.aws_request_checksum_calculation
    env["AWS_RESPONSE_CHECKSUM_VALIDATION"] = settings.aws_response_checksum_validation
    env["AWS_ACCESS_KEY_ID"] = settings.aws_access_key_id
    env["AWS_SECRET_ACCESS_KEY"] = settings.aws_secret_access_key
    
    logger.info(
        f"Uploading {source_path} to s3://{dst_key} "
        f"with command: {cmd}"
    )
    
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        result = subprocess.run(
            cmd,
            shell=True,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            logger.info(f"Successfully uploaded to {s3_uri}")
            if result.stdout:
                print(result.stdout)
            return s3_uri
        
        stdout = result.stdout
        stderr = result.stderr
        if attempt < max_attempts:
            logger.warning(
                f"Upload attempt {attempt}/{max_attempts} failed. "
                f"Error: {stderr[:200]}"
            )
            if stdout:
                print(stdout)
            continue
        
        error_msg = (
            f"Failed to upload {source_path} to s3://{dst_key} "
            f"after {attempt} attempt(s). Return code: {result.returncode}. "
            f"Error: {stderr}"
        )
        logger.error(error_msg)
        if stdout:
            print(stdout)
        raise S3UploadError(error_msg)
