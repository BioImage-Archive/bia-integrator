from __future__ import annotations

from bia_shared_datamodels import bia_data_model
from pydantic import Field

from typing import List


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
    canonical_representation: bia_data_model.ImageRepresentation = Field(
        description="""The image representation that contains the most 'ground truth' version of the image.
        Commonly this would be the one that captures the most data, both in terms of image metadata
        (e.g. records of the physical dimensions of the Field of View) but also in the visual
        fidelity of the image (e.g. has the largest field of view, or is in a data format storing the
        greatest visual detail). This is the image represetation that should be viewable on the website."""
    )
    submission_dataset: ExperimentalImagingDataset = Field(
        description="""The dataset the image was submitted with."""
    )
