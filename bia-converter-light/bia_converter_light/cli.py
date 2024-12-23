from typing import List
from pathlib import Path
import typer
from typing_extensions import Annotated

from bia_shared_datamodels.semantic_models import ImageRepresentationUseType
from .config import settings, api_client

from .io import stage_fileref_and_get_fpath, copy_local_to_s3
from .conversion import cached_convert_to_zarr_and_get_fpath, get_local_path_to_zarr
from bia_converter_light.propose_utils import (
    write_convertible_file_references_for_accession_id,
)
from . import utils
from .rendering import generate_padded_thumbnail_from_ngff_uri

import logging
from rich.logging import RichHandler

from bia_shared_datamodels import bia_data_model, semantic_models, uuid_creation
from bia_ingest.persistence_strategy import (
    persistence_strategy_factory,
    PersistenceMode,
)

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


@app.command(help="Convert image for given image representation UUID")
def convert_image(
    accession_id: Annotated[str, typer.Argument()],
    # TODO: Fix this hack. Whole interface needs changing to same as bia-converter
    file_reference_uuid: Annotated[str, typer.Argument()],
    # image_representation_uuid: Annotated[str, typer.Argument()],
    rep_to_convert: Annotated[
        ImageRepresentationUseType, typer.Option(case_sensitive=False)
    ],
    persistence_mode: Annotated[
        PersistenceMode, typer.Option(case_sensitive=False)
    ] = PersistenceMode.disk,
    update_example_image_uri: Annotated[
        bool, typer.Option("--update-example-image-uri")
    ] = False,
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

    # TODO: Restore using API Client before merging PR
    # assert isinstance(
    #    api_client, PrivateApi
    # ), f"Expected valid instance of <class 'PrivateApi'>. Got : {type(api_client)} - are your API credentials valid and/or is the API server online?"
    # representation = api_client.get_image_representation(image_representation_uuid)
    # file_reference = api_client.get_file_reference(
    #    representation.original_file_reference_uuid[0]
    # )

    ## Need accession ID Could ask for it as a parameter to CLI call, but
    ## will get from API in two calls for now
    # dataset = api_client.get_experimental_imaging_dataset(
    #    file_reference.submission_dataset_uuid
    # )
    # study = api_client.get_study(dataset.submitted_in_study_uuid)
    # accession_id = study.accession_id

    persister = persistence_strategy_factory(
        persistence_mode=persistence_mode,
        output_dir_base=settings.bia_data_dir,
        accession_id=accession_id,
        api_client=api_client,
    )
    # TODO: Fix this hack - see TODO above
    if rep_to_convert == semantic_models.ImageRepresentationUseType.INTERACTIVE_DISPLAY:
        image_format = ".ome.zarr"
    else:
        image_format = ".png"
    image_uuid = uuid_creation.create_image_uuid(
        [
            file_reference_uuid,
        ]
    )
    image_representation_uuid = uuid_creation.create_image_representation_uuid(
        image_uuid, image_format, rep_to_convert.value
    )
    # End of hack

    representation = persister.fetch_by_uuid(
        [
            image_representation_uuid,
        ],
        bia_data_model.ImageRepresentation,
    )[0]
    bia_image = persister.fetch_by_uuid(
        [representation.representation_of_uuid],
        bia_data_model.Image,
    )[0]
    file_reference = persister.fetch_by_uuid(
        [
            bia_image.original_file_reference_uuid[0],
        ],
        bia_data_model.FileReference,
    )[0]
    # dataset = persister.fetch_by_uuid(
    #    [
    #        file_reference.submission_dataset_uuid,
    #    ],
    #    bia_data_model.Dataset,
    # )
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

        attributes_from_ome = {
            "name": "attributes_from_bioformat2raw_conversion",
            "provenance": semantic_models.AttributeProvenance.bia_conversion,
            "value": pixel_metadata,
        }
        representation.attribute.append(
            semantic_models.Attribute.model_validate(attributes_from_ome)
        )

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
        # api_client.post_image_representation(representation)
        persister.persist(
            [
                representation,
            ]
        )
        message = f"Converted uploaded by submitter to ome.zarr and uploaded to S3: {representation.file_uri}"
        logger.info(message)

        return
    elif representation.use_type in (
        ImageRepresentationUseType.THUMBNAIL,
        ImageRepresentationUseType.STATIC_DISPLAY,
    ):
        ## Check for interactive display representation (ome.zarr)
        ## This has to exist before we can generate thumbnails/static display
        # eci = api_client.get_experimentally_captured_image(
        #    representation.representation_of_uuid
        # )
        # representations_for_eci = (
        #    api_client.get_image_representation_in_experimentally_captured_image(
        #        eci.uuid,
        #        page_size=DEFAULT_PAGE_SIZE,
        #    )
        # )
        # try:
        #    interactive_image_representation = next(
        #        im_rep
        #        for im_rep in representations_for_eci
        #        if len(im_rep.file_uri) > 0 and "ome.zarr" in im_rep.file_uri[0]
        #    )
        # except StopIteration as e:
        #    message = f"Cannot create thumbnail or static display without a representation with an image of ome zarr. Could not find one for experimentally captured image with UUID: {eci.uuid}"
        #    logger.error(message)
        #    raise e

        interactive_image_representation_uuid = (
            uuid_creation.create_image_representation_uuid(
                bia_image.uuid,
                ".ome.zarr",
                semantic_models.ImageRepresentationUseType.INTERACTIVE_DISPLAY.value,
            )
        )
        interactive_image_representation = persister.fetch_by_uuid(
            [
                interactive_image_representation_uuid,
            ],
            bia_data_model.ImageRepresentation,
        )[0]

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
        # representation.version += 1
        # api_client.post_image_representation(representation)
        persister.persist(
            [
                representation,
            ]
        )
        message = f"Created {representation.use_type} image and uploaded to S3: {representation.file_uri}"
        logger.info(message)

        # If STATIC_DISPLAY and update-example-uri flag set update this for dataset
        if update_example_image_uri:
            if representation.use_type == ImageRepresentationUseType.STATIC_DISPLAY:
                image = persister.fetch_by_uuid(
                    [
                        image_uuid,
                    ],
                    bia_data_model.Image,
                )[0]
                dataset = persister.fetch_by_uuid(
                    [
                        image.submission_dataset_uuid,
                    ],
                    bia_data_model.Dataset,
                )[0]
                dataset.example_image_uri.append(file_uri)
                persister.persist(
                    [
                        dataset,
                    ]
                )
                logger.info(
                    f"Updated example image uri of dataset {dataset.uuid} to {dataset.example_image_uri}"
                )
            else:
                logger.warning(
                    f"Cannot update dataset example image uri when image representation use type is {representation.use_type.value}"
                )
        return
    else:
        raise Exception(
            f"Unknown image representation use type: {representation.use_type}"
        )


@app.command()
def update_example_image_uri_for_dataset(
    accession_id: Annotated[str, typer.Argument()],
    dataset_uuid: Annotated[str, typer.Argument()],
    representation_uuid: Annotated[str, typer.Argument()],
    verbose: Annotated[bool, typer.Option("-v")] = False,
):
    persister = persistence_strategy_factory(
        persistence_mode="disk",
        output_dir_base=settings.bia_data_dir,
        accession_id=accession_id,
    )
    representation = persister.fetch_by_uuid(
        [
            representation_uuid,
        ],
        bia_data_model.ImageRepresentation,
    )[0]
    assert (
        representation.use_type
        == semantic_models.ImageRepresentationUseType.STATIC_DISPLAY
    )
    bia_image = persister.fetch_by_uuid(
        [
            representation.representation_of_uuid,
        ],
        bia_data_model.Image,
    )[0]
    assert str(bia_image.submission_of_dataset_uuid) == dataset_uuid
    dataset = persister.fetch_by_uuid(
        [
            dataset_uuid,
        ],
        bia_data_model.Dataset,
    )[0]
    dataset.example_image_uri = [representation.file_uri]
    persister.persist(
        [
            dataset,
        ]
    )


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
