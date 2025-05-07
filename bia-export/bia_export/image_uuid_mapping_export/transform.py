from uuid import UUID
from bia_integrator_api import models as api_models
from bia_export.image_uuid_mapping_export.models import (
    Image,
)
from bia_export.image_uuid_mapping_export.retrieve import (
    retrieve_images,
    retrieve_file_references,
)
import logging

logger = logging.getLogger("__main__." + __name__)


def transform_images(study_uuid: UUID) -> dict:
    image_map = {}

    api_images = retrieve_images(study_uuid)

    for api_image in api_images:

        image = transform_image(api_image)

        image_map[str(image.uuid)] = image.model_dump(mode="json")

    return image_map


def transform_image(api_image: api_models.Image) -> Image:

    file_references = retrieve_file_references(api_image)

    image_dict = api_image.model_dump() | {
        "file_reference": file_references,
    }

    return Image(**image_dict)
