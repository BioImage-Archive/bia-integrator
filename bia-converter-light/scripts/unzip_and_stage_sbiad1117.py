"""Adhoc script to stage zarr from S-BIAD1117 to s3 for web-atlas"""

import logging
from pathlib import Path

from bia_converter_light.config import settings
from bia_shared_datamodels import bia_data_model
from bia_converter_light.io import (
    unzip_fileref_and_get_fpath,
    stage_fileref_and_get_fpath,
    copy_local_to_s3,
)
from bia_converter_light import utils

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Image representations had been created on my local machine using v2
# of the API. These will be used to create the urls for s3.

# Load image representations from file
accession_id = "S-BIAD1117"
bia_data_dir = Path(settings.bia_data_dir)
image_representation_base_path = bia_data_dir / "image_representation" / accession_id
image_representation_paths = [
    im_rep_path
    for im_rep_path in image_representation_base_path.glob("*.json")
    if im_rep_path.read_text().find("INTERACTIVE_DISPLAY") >= 0
]

for im_rep_path in image_representation_paths:
    representation = bia_data_model.ImageRepresentation.model_validate_json(
        im_rep_path.read_text()
    )
    if representation.image_format is None or representation.image_format == "":
        representation.image_format = ".zarr"

    # Get file reference for image representation
    file_reference_uuid = representation.original_file_reference_uuid[0]
    file_reference_path = (
        bia_data_dir / "file_reference" / accession_id / f"{file_reference_uuid}.json"
    )
    file_reference = bia_data_model.FileReference.model_validate_json(
        file_reference_path.read_text()
    )
    local_path_to_uploaded_by_submitter_rep = stage_fileref_and_get_fpath(
        file_reference
    )

    # Unzip file reference for image representation
    unzipped_zarr_path = unzip_fileref_and_get_fpath(
        representation, local_path_to_uploaded_by_submitter_rep
    )

    # Attempt to get metadata
    try:
        pixel_metadata = utils.get_ome_zarr_pixel_metadata(
            local_path_to_uploaded_by_submitter_rep
        )

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
    except Exception as e:
        logger.error(f"Error trying to get metadata. Exception was: {e}")

    # Stage to S3
    file_uri = copy_local_to_s3(
        unzipped_zarr_path,
        utils.create_s3_uri_suffix_for_image_representation(
            accession_id, representation
        ),
    )

    # Update uri of image representation
    representation.file_uri = [
        file_uri + "/0",
    ]

    # Persist image representation
    representation.version += 1
    im_rep_path.write_text(representation.model_dump_json(indent=2))
    message = f"Converted uploaded by submitter to ome.zarr and uploaded to S3: {representation.file_uri}"
    logger.info(message)
