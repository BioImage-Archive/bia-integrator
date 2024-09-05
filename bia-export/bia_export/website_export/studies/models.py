from __future__ import annotations

from bia_export.website_export.website_models import (
    BioSample,
    ImageAcquisition,
    SpecimenGrowthProtocol,
    SpecimenImagingPreparationProtocol,
    CLIContext,
)

from bia_shared_datamodels import bia_data_model
from pydantic import BaseModel, Field


from typing import List, Optional, Type


class ImageDataset(BaseModel):
    file_count: int = Field(description="Count of file references in the dataset")
    image_count: int = Field(description="Count of images in the dataset")
    file_type_aggregation: list = Field(
        description="List of different file type extensions in the dataset."
    )


class ExperimentalImagingDataset(
    bia_data_model.ExperimentalImagingDataset, ImageDataset
):
    acquisition_process: List[ImageAcquisition] = Field(
        description="""Processes involved in the creation of the images and files in this dataset."""
    )
    specimen_imaging_preparation_protocol: List[SpecimenImagingPreparationProtocol] = (
        Field(
            description="""Processes involved in the preprapartion of the samples for imaged."""
        )
    )
    biological_entity: List[BioSample] = Field(
        description="""The biological entity or entities that were imaged."""
    )
    specimen_growth_protocol: Optional[List[SpecimenGrowthProtocol]] = Field(
        default_factory=list,
        description="""Processes involved in the growth of the samples that were then imaged.""",
    )
    image: List[bia_data_model.ExperimentallyCapturedImage] = Field(
        default_factory=list,
        description="List of image associated with the dataset.",
    )


class ImageAnnotationDataset(bia_data_model.ImageAnnotationDataset, ImageDataset):
    annotation_method: List[bia_data_model.AnnotationMethod] = Field(
        description="""The process(es) that were performed to create the annotated data."""
    )
    image: List[bia_data_model.DerivedImage] = Field(
        default_factory=list,
        description="List of image associated with the dataset.",
    )


class Study(bia_data_model.Study):
    experimental_imaging_component: Optional[List[ExperimentalImagingDataset]] = Field(
        default_factory=list,
        description="""An experimental imaging dataset of that is associated with the study.""",
    )
    image_annotation_component: Optional[List[ImageAnnotationDataset]] = Field(
        default_factory=list,
        description="""An image annotation dataset of that is associated with the study.""",
    )


class CLIContext(CLIContext):
    dataset_file_aggregate_data: dict = Field(
        default_factory=dict,
        description="Image & File Reference counts & types for each Dataset",
    )
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
