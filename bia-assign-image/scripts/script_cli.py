import re
from pathlib import Path
import json
from typing import Annotated
import typer
from bia_assign_image.api_client import (
    ApiTarget,
)
from scripts.map_image_related_artefacts_to_2025_04_models import (
    map_image_related_artefacts_to_2025_04_models,
)

# For read only client

import logging

app = typer.Typer()
map_app = typer.Typer()
app.add_typer(
    map_app,
    name="map",
    help="Map image related artefacts to 2025/04 models",
)

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
def map2(
    file_reference_mapping_path: Annotated[Path, typer.Argument()],
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.local,
    dryrun: Annotated[bool, typer.Option()] = False,
) -> str:
    file_reference_mappings = json.loads(file_reference_mapping_path.read_text())

    for file_reference_mapping in file_reference_mappings.values():
        # file_references = image_to_process.pop("file_references", {})
        # image_representations = image_to_process.pop("image_representation", {})
        accession_id = _get_accession_id(file_reference_mapping)

        if accession_id:
            # mapped_artefacts = map_image_related_artefacts_to_2025_04_models(
            map_image_related_artefacts_to_2025_04_models(
                file_reference_mapping,
                accession_id,
                api_target,
            )


@map_app.command(help="Map image related artefacts to 2025/04 models")
def map(
    file_reference_mapping_path: Annotated[Path, typer.Argument()],
    api_target: Annotated[
        ApiTarget, typer.Option("--api", "-a", case_sensitive=False)
    ] = ApiTarget.prod,
    dryrun: Annotated[bool, typer.Option()] = False,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    """Map image related artefacts to 2025/04 models"""

    if verbose:
        logger.setLevel(logging.DEBUG)


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
