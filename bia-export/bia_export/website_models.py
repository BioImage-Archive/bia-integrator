from __future__ import annotations
from pydantic import Field, BaseModel
from typing import List, Optional
from bia_shared_datamodels import bia_data_model


class Study(bia_data_model.Study):
    experimental_imaging_component: Optional[List[ExperimentalImagingDataset]] = Field(
        default_factory=list,
        description="""A dataset of that is associated with the study.""",
    )


class ExperimentalImagingDataset(bia_data_model.ExperimentalImagingDataset):
    acquisition_process: list[ImageAcquisition] = Field(
        description="""Processes involved in the creation of the images and files in this dataset."""
    )
    specimen_imaging_preparation_protocol: list[SpecimenImagingPrepartionProtocol] = (
        Field(
            description="""Processes involved in the preprapartion of the samples for imaged."""
        )
    )
    biological_entity: list[BioSample] = Field(
        description="""The biological entity or entities that were imaged."""
    )
    specimen_growth_protocol: Optional[list[SpecimenGrowthProtocol]] = Field(
        default_factory=list,
        description="""Processes involved in the growth of the samples that were then imaged.""",
    )


class DetailSection(BaseModel):
    default_open: bool = Field()


class ImageAcquisition(bia_data_model.ImageAcquisition, DetailSection):
    pass


class BioSample(bia_data_model.BioSample, DetailSection):
    pass


class SpecimenGrowthProtocol(bia_data_model.SpecimenGrowthProtocol, DetailSection):
    pass


class SpecimenImagingPrepartionProtocol(
    bia_data_model.SpecimenImagingPrepartionProtocol, DetailSection
):
    pass


class Specimen(bia_data_model.Specimen):
    imaging_preparation_protocol: List[SpecimenImagingPrepartionProtocol] = Field()
    sample_of: List[BioSample] = Field()
    growth_protocol: List[SpecimenGrowthProtocol] = Field()


class ExperimentallyCapturedImage(bia_data_model.ExperimentallyCapturedImage):
    acquisition_process: List[ImageAcquisition] = Field()
    subject: Specimen = Field()
