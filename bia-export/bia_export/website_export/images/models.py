from __future__ import annotations

from bia_shared_datamodels import bia_data_model
from pydantic import Field
from ..website_models import CLIContext
from typing import List, Optional


class ExperimentalImagingDataset(bia_data_model.ExperimentalImagingDataset):
    submitted_in_study: bia_data_model.Study = Field(
        description="""The study the dataset was submitted in."""
    )


class Specimen(bia_data_model.Specimen):
    imaging_preparation_protocol: List[
        bia_data_model.SpecimenImagingPreparationProtocol
    ] = Field(description="""How the biosample was prepared for imaging.""")
    sample_of: List[bia_data_model.BioSample] = Field(
        description="""The biological matter that sampled to create the specimen."""
    )
    growth_protocol: List[bia_data_model.SpecimenGrowthProtocol] = Field(
        description="""How the specimen was grown, e.g. cell line cultures, crosses or plant growth.""",
    )


class ExperimentallyCapturedImage(bia_data_model.ExperimentallyCapturedImage):
    acquisition_process: List[bia_data_model.ImageAcquisition] = Field(
        description="""The processes involved in the creation of the image."""
    )
    subject: Specimen = Field(
        description="""The specimen that was prepared for and captured in the field of view of the image."""
    )
    representation: Optional[List[bia_data_model.ImageRepresentation]] = Field(
        default_factory=list,
        description="""The concrete image representations of the image.""",
    )


class ImageCLIContext(CLIContext):
    image_to_rep_uuid_map: dict = Field(
        default_factory=dict,
        description="Image uuid to canonical representation uuid map in order to not re-read a lot of json files.",
    )
