import json
import logging
from pathlib import Path

import typer
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels.linked_data.utils import load_bia_ontology

from ro_crate_ingest.validator.file_list import FileListValidator
from ro_crate_ingest.validator.rdf_graph import ContextValidator
from ro_crate_ingest.validator.ro_crate_metadata_objects import (
    IDValidator,
    ModelTypeValidator,
)
from ro_crate_ingest.validator.ro_crate_standard import (
    ReadableMetadataValidator,
    SHACLValidator,
)
from ro_crate_ingest.validator.validator import ValidationResult, Validator

logger = logging.getLogger("__main__." + __name__)
logging.getLogger().setLevel(logging.INFO)


def bia_roc_validation(ro_crate_directory: Path, file_mode: FileListValidator.FileLocationMode):

    metadata_path = ro_crate_directory / "ro-crate-metadata.json"

    logging.info(f"Perfoming generic ro-crate validation of {ro_crate_directory}")
    validate(SHACLValidator.SHACLValidator(ro_crate_directory))
    validate(ReadableMetadataValidator.ReadableMetadataValidator(metadata_path))

    with open(metadata_path, "r") as f:
        ro_crate_json = json.load(f)

    graph: list[dict] = ro_crate_json["@graph"]
    context = ro_crate_json["@context"]

    validate(ContextValidator.ContextValidator(context))

    logging.info(f"Validating ro-crate objects under in the @graph of {metadata_path}")
    validate(IDValidator.IDValidator(graph)).validated_object
    ro_crate_objects: dict[str, ROCrateModel] = validate(
        ModelTypeValidator.ModelTypeValidator(graph, context)
    ).validated_object

    bia_ontology = load_bia_ontology()

    validate(
        FileListValidator.FileListValidator(
            ro_crate_objects, ro_crate_directory, bia_ontology, file_location_mode=file_mode
        )
    )


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
