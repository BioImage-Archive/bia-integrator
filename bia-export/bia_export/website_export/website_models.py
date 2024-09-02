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
    file_count: int = Field(description="Count of file references in the dataset")
    image_count: int = Field(description="Count of images in the dataset")
    file_type_aggregation: list = Field(
        description="List of different file type extensions in the dataset."
    )
    image: List[bia_data_model.ExperimentallyCapturedImage] = Field(
        default_factory=list,
        description="List of different file type extensions in the dataset.",
    )


class DetailSection(BaseModel):
    default_open: bool = Field(
        description="""Whether a details section on the website should default 
        to being open or closed when the page loads. Normally False if the
        section was previously shown higher up the page (e.g. a Biosample is
        reused across multiple study components)."""
    )


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
    imaging_preparation_protocol: List[SpecimenImagingPreparationProtocol] = Field(
        description="""How the biosample was prepared for imaging."""
    )
    sample_of: List[BioSample] = Field(
        description="""The biological matter that sampled to create the specimen."""
    )
    growth_protocol: List[SpecimenGrowthProtocol] = Field(
        description="""How the specimen was grown, e.g. cell line cultures, crosses or plant growth.""",
    )


class ExperimentallyCapturedImage(bia_data_model.ExperimentallyCapturedImage):
    acquisition_process: List[ImageAcquisition] = Field(
        description="""The processes involved in the creation of the image."""
    )
    subject: Specimen = Field(
        description="""The specimen that was prepared for and captured in the field of view of the image."""
    )
    canonical_representation: bia_data_model.ImageRepresentation = Field(
        description="""The image representation that contains the most 'ground truth' version of the image.
        Commonly this would be the one that captures the most data, both in terms of image metadata
        (e.g. records of the physical dimensions of the Field of View) but also in the visual
        fidelity of the image (e.g. has the largest field of view, or is in a data format storing the
        greatest visual detail). This is the image represetation that should be viewable on the website."""
    )


class StudyCreationContext(BaseModel):
    # This class is used by the CLI to carry around various pieces of contextual information for the different modes the CLI can be run with.

    # Local Processing Fields
    root_directory: Path = Field(default=None)
    accession_id: str = Field(default=None)
    dataset_file_aggregate_data: dict = Field(
        default_factory=dict,
        description="Image & File Reference counts & types for each Dataset",
    )
    image_to_canonical_rep_uuid_map: dict = Field(
        default_factory=dict,
        description="Image uuid to canonical representation uuid map in order to not re-read a lot of json files.",
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
