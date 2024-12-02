from typing import Type
from rich.table import Table
from rich.text import Text

from rich_tools import table_to_df
from pydantic import BaseModel, Field
import logging
from pathlib import Path
from bia_ingest.biostudies.biostudies_processing_version import (
    BioStudiesProcessingVersion,
)

logger = logging.getLogger("__main__." + __name__)


class CLIResult(BaseModel):
    pass


class IngestionResult(CLIResult):
    ProcessingVersion: BioStudiesProcessingVersion = (
        BioStudiesProcessingVersion.FALLBACK
    )
    Study_CreationCount: int = Field(default=0)
    Study_ValidationErrorCount: int = Field(default=0)
    Dataset_CreationCount: int = Field(default=0)
    Dataset_ValidationErrorCount: int = Field(default=0)
    Affiliation_CreationCount: int = Field(default=0)
    Affiliation_ValidationErrorCount: int = Field(default=0)
    Contributor_CreationCount: int = Field(default=0)
    Contributor_ValidationErrorCount: int = Field(default=0)
    FileReference_CreationCount: int = Field(default=0)
    FileReferenceValidation_ErrorCount: int = Field(default=0)
    BioSample_CreationCount: int = Field(default=0)
    BioSample_ValidationErrorCount: int = Field(default=0)
    SpecimenImagingPreparationProtocol_CreationCount: int = Field(default=0)
    SpecimenImagingPreparationProtocol_ValidationErrorCount: int = Field(default=0)
    Specimen_CreationCount: int = Field(default=0)
    Specimen_ValidationErrorCount: int = Field(default=0)
    ImageAcquisitionProtocol_CreationCount: int = Field(default=0)
    ImageAcquisitionProtocol_ValidationErrorCount: int = Field(default=0)
    AnnotationMethod_CreationCount: int = Field(default=0)
    AnnotationMethod_ValidationErrorCount: int = Field(default=0)
    AnnotationFile_CreationCount: int = Field(default=0)
    AnnotationFile_ValidationErrorCount: int = Field(default=0)
    ImageAnalysisMethod_CreationCount: int = Field(default=0)
    ImageAnalysisMethod_ValidationErrorCount: int = Field(default=0)
    ImageCorrelationMethod_CreationCount: int = Field(default=0)
    ImageCorrelationMethod_ValidationErrorCount: int = Field(default=0)
    RenderedView_CreationCount: int = Field(default=0)
    RenderedView_ValidationErrorCount: int = Field(default=0)
    Channel_CreationCount: int = Field(default=0)
    Channel_ValidationErrorCount: int = Field(default=0)
    Organism_CreationCount: int = Field(default=0)
    Organism_ValidationErrorCount: int = Field(default=0)
    Protocol_CreationCount: int = Field(default=0)
    Protocol_ValidationErrorCount: int = Field(default=0)
    ExternalLink_CreationCount: int = Field(default=0)
    ExternalLink_ValidationErrorCount: int = Field(default=0)
    Contributor_CreationCount: int = Field(default=0)
    Contributor_ValidationErrorCount: int = Field(default=0)
    Organisation_CreationCount: int = Field(default=0)
    Organisation_ValidationErrorCount: int = Field(default=0)
    Uncaught_Exception: str = Field(default="")


def tabulate_ingestion_errors(
    dict_of_results: dict[str, IngestionResult], include_object_count=False
) -> Table:

    table = Table()
    headers = ["Accession ID", "Processing Mode", "Status", "Error: Count;"]

    if include_object_count:
        for field in IngestionResult.model_fields:
            if field.endswith("_CreationCount"):
                headers.append(field.removesuffix("_CreationCount"))

    for header in headers:
        table.add_column(header, overflow="fold")

    for accession_id_key, result in dict_of_results.items():
        error_message = ""
        result_dict = result.model_dump()
        for field, value in result_dict.items():
            if field.endswith("ValidationErrorCount") and (value > 0):
                error_message += f"{field}: {value}; "

        if result.ProcessingVersion == BioStudiesProcessingVersion.V4:
            if result.Dataset_CreationCount == 0:
                error_message += "No datasets were created; "

            rembi_object_creation_count = [
                result.BioSample_CreationCount,
                result.SpecimenImagingPreparationProtocol_CreationCount,
                result.ImageAcquisitionProtocol_CreationCount,
            ]
            if any(rembi_object_creation_count) and not all(
                rembi_object_creation_count
            ):
                error_message += "Incomplete REMBI objects created; "

            if (
                not any(rembi_object_creation_count)
                and not result.AnnotationMethod_CreationCount
                and not result.Protocol_CreationCount
            ):
                error_message += "No creation protocols created; "

        if result.Uncaught_Exception:
            error_message += f"Uncaught exception: {result.Uncaught_Exception}"

        if error_message == "":
            status = Text("Success")
            status.stylize("green")
        else:
            status = Text("Failures")
            status.stylize("red")
            error_message = Text(error_message)
            error_message.stylize("red")

        row_info = [accession_id_key, result.ProcessingVersion, status, error_message]

        if include_object_count:
            for header in headers[4:]:
                row_info.append(str(result_dict[header + "_CreationCount"]))

        table.add_row(*row_info)

    return table


def write_table(table: Table, location: str):
    df = table_to_df(table, remove_markup=False)
    df.to_csv(location, index=False)
    print(f"Written result table to: {Path(location).absolute()}")


def log_model_creation_count(
    model_class: Type[BaseModel], count: int, valdiation_error_tracking: CLIResult
) -> None:
    logger.info(f"Created {model_class.__name__}. Count: {count}")
    field_name = f"{model_class.__name__}_CreationCount"
    valdiation_error_tracking.__setattr__(
        field_name, valdiation_error_tracking.__getattribute__(field_name) + count
    )


def log_failed_model_creation(
    model_class: Type[BaseModel], valdiation_error_tracking: CLIResult
) -> None:
    logger.error(f"Failed to create {model_class.__name__}")
    logger.debug("Pydantic Validation Error:", exc_info=True)
    field_name = f"{model_class.__name__}_ValidationErrorCount"
    valdiation_error_tracking.__setattr__(
        field_name, valdiation_error_tracking.__getattribute__(field_name) + 1
    )
