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
    
    images_list = settings.api_client.get_study_images_api_study_uuid_images_get(study_accession_id, limit=10**6)

    return {image.accession_id: image for image in images_list}

def get_image(accession_id: str) -> api_models.BIAImage:
    """Return all images stored on disk for the given accession."""
    
    image = settings.api_client.get_image_api_images_image_uuid_get(accession_id)

    return image
