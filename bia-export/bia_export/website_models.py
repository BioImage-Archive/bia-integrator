from __future__ import annotations
from pydantic import Field
from typing import List, Optional
from bia_shared_datamodels import bia_data_model


class Study(bia_data_model.Study):
    experimental_imaging_component: Optional[List[ExperimentalImagingDataset]] = Field(default_factory=list, description="""A dataset of that is associated with the study.""")

class ExperimentalImagingDataset(bia_data_model.ExperimentalImagingDataset):
    acquisition_process: list[bia_data_model.ImageAcquisition] = Field(
        description="""Processes involved in the creation of the images and files in this dataset."""
    )
    specimen_imaging_preparation_protocol: list[bia_data_model.SpecimenImagingPrepartionProtocol] = Field(
        description="""Processes involved in the preprapartion of the samples for imaged."""
    )
    biological_entity: list[bia_data_model.BioSample] = Field(
        description="""The biological entity or entities that were imaged."""
    )
    specimen_growth_protocol: Optional[list[bia_data_model.SpecimenImagingPrepartionProtocol]] = Field(
        description="""Processes involved in the growth of the samples that were then imaged."""
    )

