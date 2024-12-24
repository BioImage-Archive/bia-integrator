# All code in this module originate from bia-converter/bia_converter/io.py
from typing import Tuple
import logging
import subprocess
from uuid import UUID
from pathlib import Path


from .config import settings
from bia_shared_datamodels import bia_data_model

logger = logging.getLogger(__name__)


def run_zarr_conversion(input_fpath, output_dirpath):
    """Convert the local file at input_fpath to Zarr format, in a directory specified by
    output_dirpath"""

    zarr_cmd = f'export JAVA_HOME={settings.bioformats2raw_java_home} && {settings.bioformats2raw_bin} "{input_fpath}" "{output_dirpath}"'

    logger.info(f"Converting with {zarr_cmd}")

    retval = subprocess.run(
        zarr_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert (
        retval.returncode == 0
    ), f"Error converting to zarr: {retval.stderr.decode('utf-8')}"


def cached_convert_to_zarr_and_get_fpath(image_representation, input_fpath):
    zarr_fpath = get_local_path_to_zarr(image_representation.uuid)
    dst_dir_basepath = zarr_fpath.parent
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)

    if not zarr_fpath.exists():
        run_zarr_conversion(input_fpath, zarr_fpath)

    return zarr_fpath


def get_local_path_to_zarr(image_representation_uuid: [str | UUID]) -> Path:
    return (
        settings.cache_root_dirpath / "zarr" / f"{image_representation_uuid}.ome.zarr"
    )


def convert_to_zarr(
    file_reference: bia_data_model.FileReference,
) -> bia_data_model.ImageRepresentation:
    """Create zarr image of file reference"""

    local_path_to_uploaded_by_submitter_rep = stage_fileref_and_get_fpath(
        file_reference
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
    api_client.post_image_representation(representation)
    message = f"Converted uploaded by submitter to ome.zarr and uploaded to S3: {representation.file_uri}"
    logger.info(message)

    return representation


def convert_to_png(
    file_reference: bia_data_model.FileReference,
    size: Tuple[int, int],
) -> bia_data_model.ImageRepresentation:
    """Create png image of file reference"""

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
    local_path_to_zarr = get_local_path_to_zarr(interactive_image_representation.uuid)
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
