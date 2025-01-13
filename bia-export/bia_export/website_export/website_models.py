from __future__ import annotations
from pydantic import Field, BaseModel
from typing import List, Optional
from bia_integrator_api import models as api_models
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


class ImageAcquisitionProtocol(api_models.ImageAcquisitionProtocol, DetailSection):
    pass


class BioSample(api_models.BioSample, DetailSection):
    growth_protocol: Optional[api_models.Protocol] = Field(
        description="""How the specimen was grown, e.g. cell line cultures, crosses or plant growth.""",
        default=None,
    )


class Protocol(api_models.Protocol, DetailSection):
    pass


class AnnotationMethod(api_models.AnnotationMethod, DetailSection):
    pass


class SpecimenImagingPreparationProtocol(
    api_models.SpecimenImagingPreparationProtocol, DetailSection
):
    pass


class CLIContext(BaseModel):
    # This class is used by the CLI to carry around various pieces of contextual information for the different modes the CLI can be run with.

    # Local Processing Fields
    root_directory: Optional[Path] = Field(default=None)
    accession_id: Optional[str] = Field(default=None)
    # API Processing Fields
    study_uuid: Optional[UUID] = Field(default=None)
    # Fields used in both
