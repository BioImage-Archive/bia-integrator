import typer
from typing_extensions import Annotated, List

from bia_shared_datamodels.semantic_models import ImageRepresentationUseType
from .config import api_client, settings

from .io import stage_fileref_and_get_fpath, copy_local_to_s3
from .conversion import cached_convert_to_zarr_and_get_fpath, get_local_path_to_zarr
from . import utils
from .rendering import generate_padded_thumbnail_from_ngff_uri

import logging
from rich.logging import RichHandler

from bia_integrator_api.api.private_api import PrivateApi
from bia_ingest.persistence_strategy import (
    persistence_strategy_factory,
    PersistenceMode,
)
from bia_ingest.cli_logging import ImageCreationResult

from bia_converter_light.image_representation import create_image_representation

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


@app.command(help="Convert image for given image representation UUID")
def convert_image(
    image_representation_uuid: Annotated[str, typer.Argument()],
    verbose: Annotated[bool, typer.Option("-v")] = False,
) -> None:
    """Create image for supplied image rep, upload to s3 and update uri in API

    Create the actual image for the image representation and stage to S3,
    and upload the uri for the image representation in the API.

    This function is only temporary whilst the API image conversion
    using the API is being developed
    """

    if verbose:
        logger.setLevel(logging.DEBUG)

    assert isinstance(
        api_client, PrivateApi
    ), f"Expected valid instance of <class 'PrivateApi'>. Got : {type(api_client)} - are your API credentials valid and/or is the API server online?"
    representation = api_client.get_image_representation(image_representation_uuid)
    file_reference = api_client.get_file_reference(
        representation.original_file_reference_uuid[0]
    )

    # Need accession ID Could ask for it as a parameter to CLI call, but
    # will get from API in two calls for now
    dataset = api_client.get_experimental_imaging_dataset(
        file_reference.submission_dataset_uuid
    )
    study = api_client.get_study(dataset.submitted_in_study_uuid)
    accession_id = study.accession_id

    if representation.use_type == ImageRepresentationUseType.UPLOADED_BY_SUBMITTER:
        logger.warning(
            f"Cannot create/convert images for image representation of type: {representation.use_type.value} - exiting"
        )
        return
    elif representation.use_type == ImageRepresentationUseType.INTERACTIVE_DISPLAY:
        local_path_to_uploaded_by_submitter_rep = stage_fileref_and_get_fpath(
            file_reference
        )

        # Convert to zarr, get zarr metadata
        local_path_to_zarr = cached_convert_to_zarr_and_get_fpath(
            representation, local_path_to_uploaded_by_submitter_rep
        )
        pixel_metadata = utils.get_ome_zarr_pixel_metadata(local_path_to_zarr)

        def _format_pixel_metadata(key):
            value = pixel_metadata.pop(key, None)
            if isinstance(value, tuple):
                value = value[0]
            if isinstance(value, str):
                value = int(value)
            return value

        representation.size_x = _format_pixel_metadata("SizeX")
        representation.size_y = _format_pixel_metadata("SizeY")
        representation.size_z = _format_pixel_metadata("SizeZ")
        representation.size_c = _format_pixel_metadata("SizeC")
        representation.size_t = _format_pixel_metadata("SizeT")

        representation.attribute |= pixel_metadata

        representation.image_format = ".ome.zarr"
        file_uri = copy_local_to_s3(
            local_path_to_zarr,
            utils.create_s3_uri_suffix_for_image_representation(
                accession_id, representation
            ),
        )
        representation.file_uri = [
            file_uri + "/0",
        ]
        representation.version += 1
        api_client.post_image_representation(representation)
        message = f"Converted uploaded by submitter to ome.zarr and uploaded to S3: {representation.file_uri}"
        logger.info(message)

        return
    elif representation.use_type in (
        ImageRepresentationUseType.THUMBNAIL,
        ImageRepresentationUseType.STATIC_DISPLAY,
    ):
        # Check for interactive display representation (ome.zarr)
        # This has to exist before we can generate thumbnails/static display
        eci = api_client.get_experimentally_captured_image(
            representation.representation_of_uuid
        )
        representations_for_eci = (
            api_client.get_image_representation_in_experimentally_captured_image(
                eci.uuid,
                page_size=DEFAULT_PAGE_SIZE,
            )
        )
        try:
            interactive_image_representation = next(
                im_rep
                for im_rep in representations_for_eci
                if len(im_rep.file_uri) > 0 and "ome.zarr" in im_rep.file_uri[0]
            )
        except StopIteration as e:
            message = f"Cannot create thumbnail or static display without a representation with an image of ome zarr. Could not find one for experimentally captured image with UUID: {eci.uuid}"
            logger.error(message)
            raise e

        # Check for local path to zarr and use if it exists
        local_path_to_zarr = get_local_path_to_zarr(
            interactive_image_representation.uuid
        )
        if local_path_to_zarr.exists():
            source_uri = f"{local_path_to_zarr / '0'}"
            logger.info(
                f"Cached version of required ome.zarr exists locally at {source_uri}. Using this instead of S3 version"
            )
        else:
            source_uri = interactive_image_representation.file_uri[0]
            logger.info(
                f"No cached version of required ome.zarr exists locally. Using {source_uri}"
            )

        # create image
        if representation.use_type == ImageRepresentationUseType.THUMBNAIL:
            dims = (256, 256)
        else:
            dims = (512, 512)
        created_image = generate_padded_thumbnail_from_ngff_uri(source_uri, dims=dims)
        created_image_path = utils.get_local_path_for_representation(
            representation.uuid, ".png"
        )
        with created_image_path.open("wb") as fh:
            created_image.save(fh)
        logger.info(
            f"Saved {representation.use_type} representation to {created_image_path}"
        )

        # upload to s3
        representation.image_format = ".png"
        s3_uri = utils.create_s3_uri_suffix_for_image_representation(
            accession_id, representation
        )
        file_uri = copy_local_to_s3(created_image_path, s3_uri)

        # update representation
        representation.file_uri = [
            file_uri,
        ]
        representation.version += 1
        api_client.post_image_representation(representation)
        message = f"Created {representation.use_type} image and uploaded to S3: {representation.file_uri}"
        logger.info(message)

        return
    else:
        raise Exception(
            f"Unknown image representation use type: {representation.use_type}"
        )


@representations_app.command(help="Create specified representations")
def create(
    accession_id: Annotated[str, typer.Argument()],
    file_reference_uuid_list: Annotated[List[str], typer.Argument()],
    persistence_mode: Annotated[
        PersistenceMode, typer.Option(case_sensitive=False)
    ] = PersistenceMode.disk,
    reps_to_create: Annotated[
        List[ImageRepresentationUseType], typer.Option(case_sensitive=False)
    ] = [
        ImageRepresentationUseType.UPLOADED_BY_SUBMITTER,
        ImageRepresentationUseType.THUMBNAIL,
        ImageRepresentationUseType.INTERACTIVE_DISPLAY,
    ],
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    """Create representations for specified file reference(s)"""

    if verbose:
        logger.setLevel(logging.DEBUG)

    result_summary = {}

    persister = persistence_strategy_factory(
        persistence_mode,
        output_dir_base=settings.bia_data_dir,
        accession_id=accession_id,
        api_client=api_client,
    )

    result_summary = ImageCreationResult()
    for file_reference_uuid in file_reference_uuid_list:
        print(
            f"[blue]-------- Starting creation of image representations for file reference {file_reference_uuid} of {accession_id} --------[/blue]"
        )

        for representation_use_type in reps_to_create:
            logger.debug(
                f"starting creation of {representation_use_type.value} for file reference {file_reference_uuid}"
            )
            image_representation = create_image_representation(
                [
                    file_reference_uuid,
                ],
                representation_use_type=representation_use_type,
                result_summary=result_summary,
                persister=persister,
            )
            if image_representation:
                message = f"COMPLETED: Creation of image representation {representation_use_type.value} for file reference {file_reference_uuid} of {accession_id}"
            else:
                message = f"WARNING: Could NOT create image representation {representation_use_type.value} for file reference {file_reference_uuid} of {accession_id}"
            logger.debug(message)

    successes = ""
    errors = ""
    for item_name in result_summary.model_fields:
        item_value = getattr(result_summary, item_name)
        if item_name.endswith("CreationCount") and item_value > 0:
            successes += f"{item_name}: {item_value}\n"
        elif item_name.endswith("ErrorCount") and item_value > 0:
            errors += f"{item_name}: {item_value}\n"
    print(f"\n\n[green]--------- Successes ---------\n{successes}[/green]")
    print(f"\n\n[red]--------- Errors ---------\n{errors}[/red]")


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
