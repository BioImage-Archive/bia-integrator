from __future__ import annotations

from bia_shared_datamodels import bia_data_model
from pydantic import Field


class ExperimentalImagingDataset(bia_data_model.ExperimentalImagingDataset):
    submitted_in_study: bia_data_model.Study = Field()


class ExperimentalImagingDataset(bia_data_model.ExperimentalImagingDataset):
    submitted_in_study: bia_data_model.Study = Field()
