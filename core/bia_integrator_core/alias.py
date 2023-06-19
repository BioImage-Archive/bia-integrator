import logging
from typing import List

from openapi_client import models as api_models
from bia_integrator_core.image import get_image, update_image


logger = logging.getLogger(__name__)
    

def persist_image_alias(image_accno: str, alias: api_models.BIAImageAlias):
    img = get_image(image_accno)
    img.image_aliases.append(alias)
    update_image(img)

def get_aliases(image_accno: str) -> List[api_models.BIAImageAlias]:    
    img = get_image(image_accno)

    return img.image_aliases