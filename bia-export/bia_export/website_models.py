from __future__ import annotations
from pydantic import Field
from typing import List, Optional
from bia_shared_datamodels import bia_data_model


class Study(bia_data_model.Study):
    experimental_imaging_component: Optional[List[ExperimentalImagingDataset]] = Field(default_factory=list, description="""A dataset of that is associated with the study.""")

class ExperimentalImagingDataset(bia_data_model.ExperimentalImagingDataset):
    pass