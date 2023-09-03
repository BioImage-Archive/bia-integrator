import logging
from typing import List

from openapi_client import models as api_models
from .image import get_image, update_image
from .config import settings

logger = logging.getLogger(__name__)

def persist_image_representation(image_uuid: str, representation: api_models.BIAImageRepresentation):
    """Persist the representation to disk."""

    settings.api_client.create_image_representation(image_uuid, representation)

def get_representations(image_uuid: str) -> List[api_models.BIAImageRepresentation]:
    """Return all representations stored on disk for the given accession/image."""
    
    image = get_image(image_uuid)
    return image.representations