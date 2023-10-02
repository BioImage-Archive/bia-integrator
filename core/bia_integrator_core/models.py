from bia_integrator_api import models as api_models
from typing import List

class BIAStudy(api_models.BIAStudy):
    images: List[api_models.BIAImage]
    file_references: List[api_models.FileReference]