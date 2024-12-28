from typing import List
import csv
from pathlib import Path
from uuid import UUID
import typer
from typing_extensions import Annotated

from bia_shared_datamodels.semantic_models import ImageRepresentationUseType
from bia_integrator_api.exceptions import ApiException
from bia_integrator_api import PrivateApi
from bia_assign_image.cli import assign as assign_image
from bia_converter_light.config import api_client
from bia_converter_light.conversion import (
    convert_to_zarr,
    convert_to_png,
)

from bia_converter_light.propose_utils import (
    write_convertible_file_references_for_accession_id,
)

import logging
from rich.logging import RichHandler

from bia_shared_datamodels import uuid_creation

app = typer.Typer()


logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
)

# Set default page size for API queries
DEFAULT_PAGE_SIZE = 10000

logger = logging.getLogger()

representations_app = typer.Typer()
app.add_typer(
    representations_app,
    name="representations",
    help="Create specified representations",
)


def validate_propose_inputs(
    accession_ids: list[str] = None, accession_ids_path: Path = None
):
    """Validate that only one of accession_ids or file_path is provided."""
    if accession_ids and accession_ids_path:
        typer.echo(
            "Error: Provide either a list of accession IDs or a file path, not both.",
            err=True,
        )
        raise typer.Exit(code=1)
    if not accession_ids and not accession_ids_path:
        typer.echo(
            "Error: You must provide either a list of accession IDs or a file path.",
            err=True,
        )
        raise typer.Exit(code=1)


def ensure_assigned(image_uuid):
    """Ensure Image and corresponding UPLOADED_BY_USER representation exist"""
    try:
        bia_image = api_client.get_image(image_uuid)
    except ApiException:
        logger.warning(
            f"Could not find Image with uuid {image_uuid}. Attempting creation"
        )
        assign_image(file_reference_uuid)


def get_conversion_details(conversion_details_path: Path) -> List[dict]:
    with conversion_details_path.open("r") as fid:
        field_names = [
            "accession_id",
            "study_uuid",
            "file_path",
            "file_reference_uuid",
            "size_in_bytes",
            "size_human_readable",
        ]
        reader = csv.DictReader(fid, fieldnames=field_names, delimiter="\t")
        conversion_details = [row for row in reader]
    return conversion_details


def convert_file_reference_to_image_representation(
    accession_id: str,
    file_reference_uuid: str,
    use_type: ImageRepresentationUseType,
    verbose: bool = False,
) -> None:
    """Convert file ref to image rep of use type. Upload to s3

    Create the actual image for the image representation and stage to S3,
    and persist the image representation in the API.

    This function is only temporary whilst the API image conversion
    using the API is being developed
    """

    if verbose:
        logger.setLevel(logging.DEBUG)

    assert isinstance(
        api_client, PrivateApi
    ), f"Expected valid instance of <class 'PrivateApi'>. Got : {type(api_client)} - are your API credentials valid and/or is the API server online?"

    image_uuid = uuid_creation.create_image_uuid(
        [
            file_reference_uuid,
        ]
    )
    image_uuid = str(image_uuid)
    ensure_assigned(image_uuid)
    file_reference = api_client.get_file_reference(file_reference_uuid)

    bia_image = api_client.get_image(image_uuid)
    if use_type == ImageRepresentationUseType.INTERACTIVE_DISPLAY:
        return convert_to_zarr(accession_id, file_reference, bia_image)
    elif use_type in (
        ImageRepresentationUseType.THUMBNAIL,
        ImageRepresentationUseType.STATIC_DISPLAY,
    ):
        return convert_to_png(accession_id, file_reference, bia_image, use_type)
    else:
        logger.warning(
            f"Cannot create/convert images for image representation of type: {use_type.value} - exiting"
        )
        return


def update_example_image_uri(
    representation_uuid: [UUID | str],
    verbose: bool = False,
) -> bool:
    # pdb.set_trace()
    try:
        representation = api_client.get_image_representation(representation_uuid)
    except Exception as e:
        # raise(e)
        logger.error(f"Could not retrieve image representation. Error was {e}.")
        return False
    if representation.use_type == ImageRepresentationUseType.STATIC_DISPLAY:
        image = api_client.get_image(representation.representation_of_uuid)
        dataset = api_client.get_dataset(image.submission_dataset_uuid)
        dataset.example_image_uri.append(representation.file_uri[0])
        dataset.version += 1
        api_client.post_dataset(dataset)

        logger.info(
            f"Updated example image uri of dataset {dataset.uuid} to {dataset.example_image_uri}"
        )
        return True
    else:
        logger.warning(
            f"Cannot update dataset example image uri when image representation use type is {representation.use_type.value}"
        )
        return False


@app.command()
def update_example_image_uri_for_dataset(
    representation_uuid: Annotated[
        str,
        typer.Argument(help="UUID for a STATIC_DISPLAY representation of the dataset"),
    ],
    # TODO: Have a 'mode' option to allow replace, prepend or append
    verbose: Annotated[bool, typer.Option("-v")] = False,
):
    update_example_image_uri(representation_uuid, verbose)


@app.command()
def convert_image(
    accession_ids: Annotated[
        List[str], typer.Option("--accession-ids", "-a", help="Accession ID(s).")
    ] = ["all"],
    conversion_details_path: Annotated[
        Path,
        typer.Option(
            "--conversion-details-path",
            "-c",
            exists=True,
            help="Path to tsv file containing details needed for conversion (produced by 'propose' command).",
        ),
    ] = None,
    max_items: Annotated[int, typer.Option()] = 5,
    output_path: Annotated[Path, typer.Option()] = None,
):
    """Convert file references to image representations"""
    # The convention is to create
    # i) INTERACTIVE_DISPLAY
    # ii) THUMBNAIL
    # iii) If first image for accession ID STATIC_DISPLAY
    conversion_details = get_conversion_details(conversion_details_path)
    if accession_ids == ["all"]:
        set_accession_ids = {cd["accession_id"] for cd in conversion_details}
        accession_ids = list(set_accession_ids)
        accession_ids.sort()
    else:
        # Filter conversion details for accession IDs to process
        conversion_details_temp = [
            cd for cd in conversion_details if cd["accession_id"] in accession_ids
        ]
        conversion_details = conversion_details_temp

    accession_ids_with_static_display = set()
    for conversion_detail in conversion_details:
        accession_id = conversion_detail["accession_id"]
        file_reference_uuid = conversion_detail["file_reference_uuid"]
        for use_type in (
            ImageRepresentationUseType.INTERACTIVE_DISPLAY,
            ImageRepresentationUseType.THUMBNAIL,
        ):
            convert_file_reference_to_image_representation(
                accession_id,
                file_reference_uuid,
                use_type,
            )
        if accession_id not in accession_ids_with_static_display:
            # Get STATIC_DISPLAY
            convert_file_reference_to_image_representation(
                accession_id,
                file_reference_uuid,
                ImageRepresentationUseType.STATIC_DISPLAY,
            )
            accession_ids_with_static_display.add(accession_id)

    logger.info(conversion_details)
    print(conversion_details)


@app.command()
def propose(
    accession_ids: Annotated[
        List[str], typer.Option("--accession-ids", "-a", help="Accession ID(s).")
    ] = None,
    accession_ids_path: Annotated[
        Path,
        typer.Option(
            "--accession-ids-path",
            "-p",
            exists=True,
            help="Path to a file containing accession IDs one per line.",
        ),
    ] = None,
    max_items: Annotated[int, typer.Option()] = 5,
    output_path: Annotated[Path, typer.Option()] = None,
):
    """Propose images to convert"""

    # TODO: Make this output yaml in form of bia-converter
    # TODO: Write test

    # Get accession IDs
    validate_propose_inputs(accession_ids, accession_ids_path)
    if accession_ids_path:
        accession_ids = [a for a in accession_ids_path.read_text().strip().split("\n")]

    if not output_path:
        output_path = Path(__file__).parent.parent / "file_references_to_convert.tsv"
    if output_path.exists():
        assert output_path.is_file()
        output_path.unlink()

    for accession_id in accession_ids:
        n_lines_written = write_convertible_file_references_for_accession_id(
            accession_id,
            output_path,
            max_items,
            append=True,
        )
        logger.info(
            f"Written {n_lines_written} proposals to {output_path} for {accession_id}"
        )


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
