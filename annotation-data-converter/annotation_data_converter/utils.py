import logging

import bia_integrator_api.models as APIModels
from bia_integrator_api.api import PrivateApi

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
