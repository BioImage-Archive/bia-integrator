import logging
import os
import subprocess
from pathlib import Path

import bia_integrator_api.models as APIModels
from bia_integrator_api.api import PrivateApi

from annotation_data_converter.settings import get_settings

logger = logging.getLogger(__name__)


def generate_precomputed_annotation_path_suffix(
        annotation_data_uuid: str,
        image: APIModels.Image,
        api_client: PrivateApi, 
) -> str:
    """
    Create the part of the annotation path that can be used locally, and also will
    go after the bucket name on s3.
    """
    
    dataset = api_client.get_dataset(image.submission_dataset_uuid)
    study = api_client.get_study(dataset.submitted_in_study_uuid)
    accession_id = study.accession_id

    annotation_dir = f"annotations/{accession_id}/{image.uuid}/{annotation_data_uuid}"

    logger.info(f"Generated precomputed annotation suffix: {annotation_dir}")
    
    return annotation_dir


def sync_precomputed_annotation_to_s3(
        local_annotation_dirpath: str, 
        annotation_dirpath: str,
) -> str:
    """
    Create the s3 uri for the precomputed annotation data, 
    upload the data, and return the s3 uri.
    """

    settings = get_settings()
    bucket_name = settings.bucket_name
    endpoint_url = settings.endpoint_url

    logger.info(f"Uploading to bucket {bucket_name} with suffix {annotation_dirpath}")

    dst_key = f"{bucket_name}/{annotation_dirpath}/"

    cmd = f'aws --region us-east-1 --endpoint-url {endpoint_url} s3 sync "{local_annotation_dirpath}/" s3://{dst_key} --acl public-read'
    logger.info(f"Uploading using command {cmd}")

    env = os.environ.copy()
    env['AWS_REQUEST_CHECKSUM_CALCULATION'] = settings.aws_request_checksum_calculation
    env['AWS_RESPONSE_CHECKSUM_VALIDATION'] = settings.aws_response_checksum_validation

    subprocess.run(cmd, shell=True, env=env)

    uri = f"{endpoint_url}/{dst_key}"

    return uri
