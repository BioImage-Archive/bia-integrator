from pathlib import Path
from ro_crate_ingest.validator.graph_entities import IDValidator, ModelTypeValidator
from ro_crate_ingest.validator.validator import ValidationResult, Validator
from ro_crate_ingest.validator.ro_crate_standard import (
    ReadableMetadataValidator,
    SHACLValidator,
)
import json
import typer
import logging
from typing import Type

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

    graph = ro_crate_json.get("@graph")
    context = ro_crate_json.get("@context")

    logging.info(f"Validating ro-crate objects under in the @graph of {metadata_path}")
    validate(IDValidator.IDValidator(graph))
    validate(ModelTypeValidator.ModelTypeValidator(graph, context))

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
