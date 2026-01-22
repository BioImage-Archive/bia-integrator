from __future__ import annotations

from bia_export.website_export.website_models import (
    BioSample,
    ImageAcquisitionProtocol,
    SpecimenImagingPreparationProtocol,
    AnnotationMethod,
    Protocol,
    CLIContext,
)
from bia_integrator_api import models

from pydantic import Field

from enum import Enum

from typing import List, Optional, Type


class Dataset(models.Dataset, models.DatasetStats):
    acquisition_process: Optional[List[ImageAcquisitionProtocol]] = Field(
        description="""Processes involved in the creation of the images and files in this dataset.""",
        default_factory=list,
    )
    specimen_imaging_preparation_protocol: Optional[
        List[SpecimenImagingPreparationProtocol]
    ] = Field(
        description="""Processes involved in the preprapartion of the samples for imaging.""",
        default_factory=list,
    )
    biological_entity: Optional[List[BioSample]] = Field(
        description="""The biological entity or entities that were imaged.""",
        default_factory=list,
    )
    annotation_process: Optional[List[AnnotationMethod]] = Field(
        description="""Methods used to create the annotated image.""",
        default_factory=list,
    )
    other_creation_process: Optional[List[Protocol]] = Field(
        description="""Other protocols followed in order to create the images in this dataset.""",
        default_factory=list,
    )
    image: List[Image] = Field(
        default_factory=list,
        description="List of image associated with the dataset.",
    )


class Study(models.Study):
    dataset: Optional[List[Dataset]] = Field(
        default_factory=list,
        description="""A dataset that is associated with the study.""",
    )


class CacheUse(Enum):
    READ_CACHE = "read_cache"
    WRITE_CACHE = "write_cache"


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
            AnnotationMethod: set(),
            Protocol: set(),
        },
        description="""Tracks e.g. which BioSamples have been displayed in previous dataset sections to 
        determine whether details should default to open or closed.""",
    )
    cache_use: Optional[CacheUse] = None


class Image(models.Image):
    total_size_in_bytes: float | None = Field(
        description="""total file size in bytes""",
    )
