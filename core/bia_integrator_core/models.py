from openapi_client import models as api_models
from typing import List

class BIAStudy(api_models.BIAStudy):
    images: List[api_models.BIAImage]