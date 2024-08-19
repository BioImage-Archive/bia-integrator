from pathlib import Path
import os

from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
import logging

default_output_base = (
    f"{Path(os.environ.get('HOME', '')) / '.cache' / 'bia-integrator-data-sm'}"
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{Path(__file__).parent.parent / '.env'}",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # extra="forbid",
    )

    bia_data_dir: str = Field(default_output_base)


# class Settings:
#    def __init__(self):
#        self.bia_data_dir = default_output_base


settings = Settings()


RESULT_SUMMARY = {}

class ObjectValidationResult(BaseModel):
    StudyValidation_ErrorCount: int = Field(default=0)
    ExperimentalImagingDataseta_ValidationErrorCount: int = Field(default=0)
    AnnotationDataseta_ValidationErrorCount: int = Field(default=0)
    FileReferenceValidation_ErrorCount: int = Field(default=0)
    BioSample_ValidationErrorCount: int = Field(default=0)
    SpecimenGrowthProtocol_ValidationErrorCount: int = Field(default=0)
    SpecimenImagingPreparationProtocol_ValidationErrorCount: int = Field(default=0)
    Specimen_ValidationErrorCount: int = Field(default=0)
    DerivedImage_ValidationErrorCount: int = Field(default=0)
    AnnotationMethod_ValidationErrorCount: int = Field(default=0)
    AnnotationDataset_ValidationErrorCount: int = Field(default=0)
    AnnotationFile_ValidationErrorCount: int = Field(default=0)
    ImageAnalysisMethod_ValidationErrorCount: int = Field(default=0)
    ImageCorrelationMethod_ValidationErrorCount: int = Field(default=0)
    RenderedView_ValidationErrorCount: int = Field(default=0)
    Channel_ValidationErrorCount: int = Field(default=0)
    Organism_ValidationErrorCount: int = Field(default=0)
    ExternalLink_ValidationErrorCount: int = Field(default=0)
    Contributor_ValidationErrorCount: int = Field(default=0)
    Organisation_ValidationErrorCount: int = Field(default=0)