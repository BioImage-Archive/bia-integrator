import logging
from typing import List

from bia_integrator_core.models import BIAImageRepresentation
from .image import get_image, update_image

logger = logging.getLogger(__name__)


def persist_image_representation(image_uuid: str, representation: BIAImageRepresentation):
    """Persist the representation to disk."""

    image = get_image(image_uuid)
    image.representations.append(representation)
    update_image(image)

def get_representations(image_uuid: str) -> List[BIAImageRepresentation]:
    """Return all representations stored on disk for the given accession/image."""
    
    image = get_image(image_uuid)
    return image.representations