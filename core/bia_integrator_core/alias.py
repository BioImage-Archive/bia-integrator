import logging
from typing import List

from bia_integrator_api import models as api_models
from bia_integrator_core.image import get_image, update_image


logger = logging.getLogger(__name__)
    

def persist_image_alias(image_uuid: str, alias: api_models.BIAImageAlias, overwrite: bool = False):
    img = get_image(image_uuid)
    if img.alias and not overwrite:
        raise Exception(f"Image {image_uuid} already has alias {img.alias.name}. Unable to set alias to {alias.name}")
    img.alias = alias

    update_image(img)
