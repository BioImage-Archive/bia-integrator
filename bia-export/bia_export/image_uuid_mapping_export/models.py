from __future__ import annotations

from bia_integrator_api import models as api_models
from pydantic import Field

from typing import List


class Image(api_models.Image):
    file_reference: List[api_models.FileReference] = Field()
