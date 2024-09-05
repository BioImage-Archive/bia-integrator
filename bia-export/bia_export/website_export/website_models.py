from __future__ import annotations
from pydantic import Field, BaseModel
from typing import List, Optional, Type
from bia_shared_datamodels import bia_data_model
from uuid import UUID
from pathlib import Path
import logging

logger = logging.getLogger("__main__." + __name__)


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


class CLIContext(BaseModel):
    # This class is used by the CLI to carry around various pieces of contextual information for the different modes the CLI can be run with.

    # Local Processing Fields
    root_directory: Path = Field(default=None)
    accession_id: str = Field(default=None)
    # API Processing Fields
    study_uuid: UUID = Field(default=None)
    # Fields used in both
