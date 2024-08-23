from rich.table import Table
from rich.text import Text
from pydantic import BaseModel, Field


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


def tabulate_errors(dict_of_results: dict[str, ObjectValidationResult]) -> Table:
    table = Table("Accession ID", "Status", "Error: Count;")
    for accession_id_key, validation_result in dict_of_results.items():
        error_message = ""
        errors = validation_result.model_dump()
        for field, value in errors.items():
            if value > 0:
                error_message += f"{field}: {value}; "

        if error_message == "":
            status = Text("Success")
            status.stylize("green")
        else:
            status = Text("Failures")
            status.stylize("red")
            error_message = Text(error_message)
            error_message.stylize("red")

        table.add_row(accession_id_key, status, error_message)

    return table
