import re
from pathlib import Path
import json
from typing import Annotated
import typer
from bia_assign_image.api_client import (
    ApiTarget,
    get_api_client,
    store_object_in_api_idempotent,
)
from scripts.map_image_related_artefacts_to_2025_04_models import (
    map_image_related_artefacts_to_2025_04_models,
    contains_displayable_image_representation,
)

import logging

app = typer.Typer()

logging.basicConfig(
    #    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger()


def _get_accession_id(file_reference_mapping: dict) -> str | None:
    """Return the accession ID associated with the mapping"""

    pattern = r"^.*/(S-[A-Za-z0-9_\-]+)/.*$"
    matcher = re.compile(pattern)

    file_references = file_reference_mapping.get("file_reference")
    if file_references:
        accession_id = matcher.findall(file_references[0]["uri"])
        if accession_id:
            return accession_id[0]

    image_representations = file_reference_mapping.get("image_representation")
    if image_representations:
        for image_representation in image_representations:
            accession_id = matcher.findall(image_representation["file_uri"][0])
            if accession_id:
                return accession_id[0]

    return None


@app.command(help="Map image related artefacts to 2025/04 models")
def map_to_2025_04_models(
    file_reference_mapping_path: Annotated[Path, typer.Argument()],
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.local,
    dryrun: Annotated[bool, typer.Option()] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
):
    if verbose:
        logger.setLevel(logging.DEBUG)

    file_reference_mappings = json.loads(file_reference_mapping_path.read_text())
    api_client = get_api_client(api_target)

    n_file_reference_mappings = len(file_reference_mappings.keys())
    for counter, file_reference_mapping in enumerate(
        file_reference_mappings.values(), start=1
    ):
        # Only process if mapping contains displayable image representations
        if not contains_displayable_image_representation(file_reference_mapping):
            image_uuid = file_reference_mapping["uuid"]
            logger.info(
                f"Skipping mapping {counter} of {n_file_reference_mappings} with image_uuid {image_uuid} as it does not contain displayable image representations"
            )
            continue
        # file_references = image_to_process.pop("file_references", {})
        # image_representations = image_to_process.pop("image_representation", {})
        accession_id = _get_accession_id(file_reference_mapping)
        logger.info(
            f"Processing mapping {counter} of {n_file_reference_mappings} with accession ID: {accession_id}"
        )
        if accession_id:
            mapped_artefacts = map_image_related_artefacts_to_2025_04_models(
                file_reference_mapping,
                accession_id,
                api_target,
            )
            if mapped_artefacts.get("representation_of_image_uploaded_by_submitter"):
                store_object_in_api_idempotent(
                    api_client,
                    mapped_artefacts.get(
                        "representation_of_image_uploaded_by_submitter"
                    ),
                )
            if mapped_artefacts.get("representation_of_image_converted_to_ome_zarr"):
                store_object_in_api_idempotent(
                    api_client,
                    mapped_artefacts.get(
                        "representation_of_image_converted_to_ome_zarr"
                    ),
                )


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
