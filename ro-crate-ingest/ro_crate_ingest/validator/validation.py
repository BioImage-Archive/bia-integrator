import json
import typer
import logging

from pathlib import Path
from ro_crate_ingest.validator.ro_crate_metadata_objects import (
    FileListValidator,
    IDValidator,
    ModelTypeValidator,
    IDReferenceValidatory,
)
from ro_crate_ingest.validator.rdf_graph import (
    ContextValidator
)
from ro_crate_ingest.validator.validator import ValidationResult, Validator
from ro_crate_ingest.validator.ro_crate_standard import (
    ReadableMetadataValidator,
    SHACLValidator,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel


logger = logging.getLogger("__main__." + __name__)
logging.getLogger().setLevel(logging.INFO)


def bia_roc_validation(ro_crate_directory: Path):

    metadata_path = ro_crate_directory / "ro-crate-metadata.json"

    logging.info(f"Perfoming generic ro-crate validation of {ro_crate_directory}")
    validate(SHACLValidator.SHACLValidator(ro_crate_directory))
    validate(ReadableMetadataValidator.ReadableMetadataValidator(metadata_path))

    with open(metadata_path, "r") as f:
        ro_crate_json = json.load(f)

    # TODO: Add context validation

    graph: list[dict] = ro_crate_json["@graph"]
    context = ro_crate_json["@context"]

    x = ContextValidator.ContextValidator(context)
    x.validate()

    logging.info(f"Validating ro-crate objects under in the @graph of {metadata_path}")
    list_of_ids: list[str] = validate(IDValidator.IDValidator(graph)).validated_object
    model_objects: dict[str, ROCrateModel] = validate(
        ModelTypeValidator.ModelTypeValidator(graph, context)
    ).validated_object

    file_lists = [model_object for model_object in model_objects]

    # TODO: Add file list validation


def log_issues(validation_result: ValidationResult):
    for issue in validation_result.issues:
        if issue.location_description:
            logger.__getattribute__(issue.severity.lower())(
                f"{issue.location_description}:\n{issue.message}"
            )
        else:
            logger.__getattribute__(issue.severity.lower())(issue.message)


def validate(validator: Validator) -> ValidationResult:
    validation_result = validator.validate()
    if validation_result.result == 1:
        log_issues(validation_result)
        raise typer.Exit(1)
    else:
        logging.info(f"Passed {type(validator).__name__}.")
        return validation_result
