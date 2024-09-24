from rich.table import Table
from rich.text import Text
from pydantic import BaseModel, Field


class IngestionResult(BaseModel):
    Study_CreationCount: int = Field(default=0)
    Study_ValidationErrorCount: int = Field(default=0)
    ExperimentalImagingDataset_CreationCount: int = Field(default=0)
    ExperimentalImagingDataset_ValidationErrorCount: int = Field(default=0)
    AnnotationDataset_CreationCount: int = Field(default=0)
    AnnotationDataset_ValidationErrorCount: int = Field(default=0)
    FileReference_CreationCount: int = Field(default=0)
    FileReferenceValidation_ErrorCount: int = Field(default=0)
    BioSample_CreationCount: int = Field(default=0)
    BioSample_ValidationErrorCount: int = Field(default=0)
    SpecimenGrowthProtocol_CreationCount: int = Field(default=0)
    SpecimenGrowthProtocol_ValidationErrorCount: int = Field(default=0)
    SpecimenImagingPreparationProtocol_CreationCount: int = Field(default=0)
    SpecimenImagingPreparationProtocol_ValidationErrorCount: int = Field(default=0)
    Specimen_CreationCount: int = Field(default=0)
    Specimen_ValidationErrorCount: int = Field(default=0)
    ImageAcquisition_CreationCount: int = Field(default=0)
    ImageAcquisition_ValidationErrorCount: int = Field(default=0)
    DerivedImage_CreationCount: int = Field(default=0)
    DerivedImage_ValidationErrorCount: int = Field(default=0)
    AnnotationMethod_CreationCount: int = Field(default=0)
    AnnotationMethod_ValidationErrorCount: int = Field(default=0)
    ImageAnnotationDataset_CreationCount: int = Field(default=0)
    ImageAnnotationDataset_ValidationErrorCount: int = Field(default=0)
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
    ExternalLink_CreationCount: int = Field(default=0)
    ExternalLink_ValidationErrorCount: int = Field(default=0)
    Contributor_CreationCount: int = Field(default=0)
    Contributor_ValidationErrorCount: int = Field(default=0)
    Organisation_CreationCount: int = Field(default=0)
    Organisation_ValidationErrorCount: int = Field(default=0)
    ExperimentallyCapturedImage_CreationCount: int = Field(default=0)
    ExperimentallyCapturedImage_ValidationErrorCount: int = Field(default=0)


def tabulate_errors(dict_of_results: dict[str, IngestionResult]) -> Table:
    table = Table("Accession ID", "Status", "Error: Count;")
    for accession_id_key, result in dict_of_results.items():
        error_message = ""
        result_dict = result.model_dump()
        for field, value in result_dict.items():
            if field.endswith("ValidationErrorCount") & value > 0:
                error_message += f"{field}: {value}; "

        if (
            result.ExperimentalImagingDataset_CreationCount == 0 
            & result.ImageAnnotationDataset_CreationCount == 0
        ):
            error_message += "No datasets were created; "

        if result.ExperimentalImagingDataset_CreationCount > 0:
            if not (
                result.BioSample_CreationCount == 0 
                & result.SpecimenImagingPreparationProtocol_CreationCount == 0
                & result.ImageAcquisition_CreationCount == 0
            ):
                if (
                    result.BioSample_CreationCount == 0 
                    | result.SpecimenImagingPreparationProtocol_CreationCount == 0
                    | result.ImageAcquisition_CreationCount == 0
                ):
                    error_message += "Incomplete REMBI objects created; "
            else:
                error_message += "No REMBI objects associated with Dataset; "

        if result.ImageAnnotationDataset_CreationCount > 0:
            if result.AnnotationMethod_CreationCount == 0:
                error_message += "No Annotation Method associated with Dataset; "

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
