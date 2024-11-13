from __future__ import annotations

from bia_export.website_export.website_models import (
    BioSample,
    ImageAcquisitionProtocol,
    SpecimenImagingPreparationProtocol,
    CLIContext,
)
from bia_integrator_api import models

from pydantic import BaseModel, Field


from typing import List, Optional, Type


class Dataset(models.Dataset):
    acquisition_process: Optional[List[ImageAcquisitionProtocol]] = Field(
        description="""Processes involved in the creation of the images and files in this dataset.""",
        default_factory=list,
    )
    specimen_imaging_preparation_protocol: Optional[
        List[SpecimenImagingPreparationProtocol]
    ] = Field(
        description="""Processes involved in the preprapartion of the samples for imaged.""",
        default_factory=list,
    )
    biological_entity: Optional[List[BioSample]] = Field(
        description="""The biological entity or entities that were imaged.""",
        default_factory=list,
    )
    image: List[models.Image] = Field(
        default_factory=list,
        description="List of image associated with the dataset.",
    )
    file_count: int = Field(description="Count of file references in the dataset")
    image_count: int = Field(description="Count of images in the dataset")
    file_type_aggregation: list = Field(
        description="List of different file type extensions in the dataset."
    )


class Study(models.Study):
    dataset: Optional[List[Dataset]] = Field(
        default_factory=list,
        description="""A dataset that is associated with the study.""",
    )


class StudyCLIContext(CLIContext):
    dataset_file_aggregate_data: dict = Field(
        default_factory=dict,
        description="Image & File Reference counts & types for each Dataset",
    )
    displayed_dataset_detail: dict[Type, set] = Field(
        default={
            ImageAcquisitionProtocol: set(),
            BioSample: set(),
            SpecimenImagingPreparationProtocol: set(),
        },
        description="""Tracks e.g. which BioSamples have been displayed in previous dataset sections to 
        determine whether details should default to open or closed.""",
    )
