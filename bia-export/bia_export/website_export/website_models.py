from __future__ import annotations
from pydantic import Field, BaseModel
from typing import List, Optional, Type
from bia_shared_datamodels import bia_data_model
from uuid import UUID
from pathlib import Path
import logging

logger = logging.getLogger("__main__." + __name__)


class Study(bia_data_model.Study):
    experimental_imaging_component: Optional[List[ExperimentalImagingDataset]] = Field(
        default_factory=list,
        description="""A dataset of that is associated with the study.""",
    )


class ExperimentalImagingDataset(bia_data_model.ExperimentalImagingDataset):
    acquisition_process: list[ImageAcquisition] = Field(
        description="""Processes involved in the creation of the images and files in this dataset."""
    )
    specimen_imaging_preparation_protocol: list[SpecimenImagingPreparationProtocol] = (
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
    file_count: int = Field()
    image_count: int = Field()
    file_type_aggregation: list = Field()
    image: List[bia_data_model.ExperimentallyCapturedImage] = Field(
        default_factory=list
    )


class DetailSection(BaseModel):
    default_open: bool = Field()


class ImageAcquisition(bia_data_model.ImageAcquisition, DetailSection):
    pass


class BioSample(bia_data_model.BioSample, DetailSection):
    pass


class SpecimenGrowthProtocol(bia_data_model.SpecimenGrowthProtocol, DetailSection):
    pass


class SpecimenImagingPreparationProtocol(
    bia_data_model.SpecimenImagingPreparationProtocol, DetailSection
):
    pass


class Specimen(bia_data_model.Specimen):
    imaging_preparation_protocol: List[SpecimenImagingPreparationProtocol] = Field()
    sample_of: List[BioSample] = Field()
    growth_protocol: List[SpecimenGrowthProtocol] = Field()


class ExperimentallyCapturedImage(bia_data_model.ExperimentallyCapturedImage):
    acquisition_process: List[ImageAcquisition] = Field()
    subject: Specimen = Field()


class StudyCreationContext(BaseModel):
    # Local Processing Fields
    root_directory: Path = Field(default=None)
    accession_id: str = Field(default=None)
    dataset_file_aggregate_data: dict = Field(
        default_factory=dict,
        description="Image & File Reference counts & types for each Dataset",
    )
    # API Processing Fields
    study_uuid: UUID = Field(default=None)
    # Fields used in both
    displayed_dataset_detail: dict[Type, set] = Field(
        default={
            ImageAcquisition: set(),
            BioSample: set(),
            SpecimenImagingPreparationProtocol: set(),
            SpecimenGrowthProtocol: set(),
        },
        description="""Tracks e.g. which BioSamples have been displayed in previous dataset sections to 
        determine whether details should default to open or closed.""",
    )
