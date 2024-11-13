from __future__ import annotations

from bia_integrator_api import models
from pydantic import Field


class Dataset(models.Dataset):
    submitted_in_study: models.Study = Field()
