from __future__ import annotations
from pydantic import Field
from typing import List, Optional
from bia_shared_datamodels import bia_data_model, semantic_models


class Study(semantic_models.Study, bia_data_model.DocumentMixin):
    experimental_imaging_component: Optional[List[ExperimentalImagingDataset]] = Field(default_factory=list, description="""A dataset of that is associated with the study.""")

class ExperimentalImagingDataset(semantic_models.ExperimentalImagingDataset, bia_data_model.DocumentMixin):
    pass