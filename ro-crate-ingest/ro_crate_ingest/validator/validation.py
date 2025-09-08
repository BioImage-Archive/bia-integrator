from pathlib import Path
from ro_crate_ingest.validator.graph_entities import GraphValidator
from ro_crate_ingest.validator.validator import ValidationResult
from ro_crate_ingest.validator.ro_crate_validator import BaseROCrateValidator
import json
import typer
import logging

logger = logging.getLogger("__main__." + __name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.INFO)

def bia_roc_validation(ro_crate_directory: Path):

    logging.info(f"Perfoming generic ro-crate validation of {ro_crate_directory}")
    roc_base_validation(ro_crate_directory)

    metadata_path = ro_crate_directory / "ro-crate-metadata.json"

    with open(metadata_path, "r") as f:
        ro_crate_json = json.load(f)

    # TODO: Add context validation

    logging.info(f"Validating ro-crate objects under in the @graph of {metadata_path}")
    roc_graph_object_validation(ro_crate_json)

    # TODO: Add file list validation

    logging.info("TEST")


def roc_base_validation(ro_crate_directory: Path):
    roc_base_validator = BaseROCrateValidator()
    ro_crate_graph_results = roc_base_validator.validate(ro_crate_directory)
    if ro_crate_graph_results.result == 1:
        log_issues(ro_crate_graph_results)
        raise typer.Exit(1)
    else:
        logging.info("Passed basic RO-Crate validation.")


def roc_graph_object_validation(ro_crate_json: dict):
    graph_validator = GraphValidator()
    ro_crate_graph_results = graph_validator.validate(
        ro_crate_json["@graph"], ro_crate_json["@context"]
    )
    if ro_crate_graph_results.result == 1:
        log_issues(ro_crate_graph_results)
        raise typer.Exit(1)
    else:
        logging.info("Passed validation of ro-crate objects.")


def log_issues(validation_result: ValidationResult):
    for issue in validation_result.issues:
        if issue.location_description:
            logger.__getattribute__(issue.severity.lower())(
                f"{issue.location_description}:\n{issue.message}"
            )
        else:
            logger.__getattribute__(issue.severity.lower())(issue.message)
