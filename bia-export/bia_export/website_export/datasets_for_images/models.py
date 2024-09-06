from __future__ import annotations

from bia_integrator_api import models
from pydantic import Field


class ExperimentalImagingDataset(models.ExperimentalImagingDataset):
    submitted_in_study: models.Study = Field()
