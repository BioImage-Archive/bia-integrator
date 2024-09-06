from __future__ import annotations

from bia_integrator_api import models
from pydantic import Field
from ..website_models import (
    CLIContext,
    SpecimenGrowthProtocol,
    SpecimenImagingPreparationProtocol,
    BioSample,
    ImageAcquisition,
)
from typing import List, Optional


class ExperimentalImagingDataset(models.ExperimentalImagingDataset):
    submitted_in_study: models.Study = Field(
        description="""The study the dataset was submitted in."""
    )


class Specimen(models.Specimen):
    imaging_preparation_protocol: List[SpecimenImagingPreparationProtocol] = Field(
        description="""How the biosample was prepared for imaging."""
    )
    sample_of: List[BioSample] = Field(
        description="""The biological matter that sampled to create the specimen."""
    )
    growth_protocol: List[SpecimenGrowthProtocol] = Field(
        description="""How the specimen was grown, e.g. cell line cultures, crosses or plant growth.""",
    )


class ExperimentallyCapturedImage(models.ExperimentallyCapturedImage):
    acquisition_process: List[ImageAcquisition] = Field(
        description="""The processes involved in the creation of the image."""
    )
    subject: Specimen = Field(
        description="""The specimen that was prepared for and captured in the field of view of the image."""
    )
    representation: Optional[List[models.ImageRepresentation]] = Field(
        default_factory=list,
        description="""The concrete image representations of the image.""",
    )


class ImageCLIContext(CLIContext):
    image_to_rep_uuid_map: dict = Field(
        default_factory=dict,
        description="Image uuid to canonical representation uuid map in order to not re-read a lot of json files.",
    )
