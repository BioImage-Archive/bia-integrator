import logging
from typing import List

from .config import settings
from openapi_client import models as api_models

logger = logging.getLogger(__name__)


def persist_image(image: api_models.BIAImage):
    """Persist the image to disk."""

    logger.info(f"Writing image to {image.accession_id}")
    settings.api_client.create_images_api_private_images_post([image])

def update_image(image: api_models.BIAImage):
    """Persist the image to disk."""

    image.version += 1
    settings.api_client.update_image_api_private_images_single_patch(image)

def get_images(study_accession_id: str) -> List[api_models.BIAImage]:
    """Return all images stored on disk for the given accession."""
    
    study_obj_info = settings.api_client.get_object_info_by_accession_api_object_info_by_accessions_get([study_accession_id]).pop()
    images_list = settings.api_client.get_study_images_api_study_uuid_images_get(study_obj_info.uuid, limit=10**6)

    return images_list

def get_image(image_uuid: str) -> api_models.BIAImage:
    """Return all images stored on disk for the given accession."""
    
    image = settings.api_client.get_image_api_images_image_uuid_get(image_uuid)

    return image
