from __future__ import annotations

from bia_integrator_api import models as api_models
from pydantic import Field
from ..website_models import (
    CLIContext,
    Protocol,
    SpecimenImagingPreparationProtocol,
    BioSample,
    ImageAcquisitionProtocol,
    AnnotationMethod,
)
from typing import List, Optional


class CreationProcess(api_models.CreationProcess):
    acquisition_process: List[ImageAcquisitionProtocol] = Field(
        description="""The processes involved in the experimental aquisition of the image.""",
        default_factory=list,
    )
    subject: Specimen = Field(
        description="""The specimen that was prepared for and captured in the field of view of the image.""",
        default=None,
    )
    annotation_method: List[AnnotationMethod] = Field(
        description="""The processes involved in the creation of annotation of images.""",
        default_factory=list,
    )
    protocol: List[Protocol] = Field(
        description="""Other protocols involved in the creation of the image.""",
        default_factory=list,
    )


class Specimen(api_models.Specimen):
    imaging_preparation_protocol: List[SpecimenImagingPreparationProtocol] = Field(
        description="""How the biosample was prepared for imaging."""
    )
    sample_of: List[BioSample] = Field(
        description="""The biological matter that sampled to create the specimen."""
    )


class Image(api_models.Image):
    creation_process: CreationProcess = Field(
        description="""The processes involved in creating the image"""
    )
    representation: Optional[List[api_models.ImageRepresentation]] = Field(
        default_factory=list,
        description="""The concrete image representations of the image.""",
    )
    total_physical_size: Optional[dict] = Field(
        description="""total_physical_size""",
    )


class ImageCLIContext(CLIContext):
    image_to_rep_uuid_map: dict = Field(
        default_factory=dict,
        description="Image uuid to canonical representation uuid map in order to not re-read a lot of json files.",
    )
