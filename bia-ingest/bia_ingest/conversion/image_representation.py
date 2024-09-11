import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from .utils import dict_to_uuid, get_bia_data_model_by_uuid, persist
from .experimentally_captured_image import get_experimentally_captured_image
from ..biostudies import (
    Submission,
)
from bia_shared_datamodels import bia_data_model
from bia_shared_datamodels.semantic_models import ImageRepresentationUseType

from bia_ingest.image_utils import image_utils
from bia_ingest.image_utils.io import stage_fileref_and_get_fpath, copy_local_to_s3
from bia_ingest.image_utils.conversion import cached_convert_to_zarr_and_get_fpath
from bia_ingest.image_utils.rendering import generate_padded_thumbnail_from_ngff_uri

logger = logging.getLogger("__main__." + __name__)


def create_image_representation(
    submission: Submission,
    file_reference_uuids: List[UUID],
    representation_use_type: ImageRepresentationUseType,
    result_summary: dict,
    representation_location: Optional[str] = None,
    persist_artefacts: Optional[bool] = False,
) -> bia_data_model.ImageRepresentation:
    """Create ImageRepresentation for specified FileReference(s) zarr"""

    # TODO: this should be replaced by API client and we would not need
    # accession_id
    file_references = [
        get_bia_data_model_by_uuid(uuid, bia_data_model.FileReference, submission.accno)
        for uuid in file_reference_uuids
    ]

    experimentally_captured_image = get_experimentally_captured_image(
        submission=submission,
        dataset_uuid=file_references[0].submission_dataset_uuid,
        file_paths=[fr.file_path for fr in file_references],
        result_summary=result_summary,
        persist_artefacts=persist_artefacts,
    )

    # TODO: Use bioformats or PIL for other formats (if on local disk)
    if representation_location:
        image_format = image_utils.get_image_extension(representation_location)
    else:
        image_format = ""

    pixel_metadata = {}
    total_size_in_bytes = 0
    file_uri = []
    if image_format == ".ome.zarr":
        pixel_metadata = image_utils.get_ome_zarr_pixel_metadata(
            representation_location
        )
        total_size_in_bytes = image_utils.get_total_zarr_size(representation_location)

    if representation_use_type == ImageRepresentationUseType.UPLOADED_BY_SUBMITTER:
        if total_size_in_bytes == 0:
            total_size_in_bytes = sum([fr.size_in_bytes for fr in file_references])
        # TODO: Discuss what to do if file reference is list > 1 with different paths e.g. .hdr and .img for analyze. Currently just using first file reference
        if image_format == "":
            image_format = image_utils.get_image_extension(file_references[0].file_path)
        file_uri = [fr.uri for fr in file_references]

    model_dict = {
        "image_format": image_format,
        "use_type": representation_use_type,
        "file_uri": file_uri,
        "original_file_reference_uuid": file_reference_uuids,
        "representation_of_uuid": experimentally_captured_image.uuid,
        "total_size_in_bytes": total_size_in_bytes,
        "size_x": pixel_metadata.get("SizeX", None),
        "size_y": pixel_metadata.get("SizeY", None),
        "size_z": pixel_metadata.get("SizeZ", None),
        "size_c": pixel_metadata.get("SizeC", None),
        "size_t": pixel_metadata.get("SizeT", None),
        # TODO: physical_size_? not included yet. In OME these are
        # separated into values and units whereas model expects just
        # values standardised to 'm' ...
        "attribute": {},
        "version": 1,
    }
    model_dict["uuid"] = generate_image_representation_uuid(model_dict)
    image_representation = bia_data_model.ImageRepresentation.model_validate(model_dict)

    if persist_artefacts and image_representation:
        persist(
            [
                image_representation,
            ],
            "image_representations",
            submission.accno,
        )

    return image_representation
    # return dicts_to_api_models([model_dict,], bia_data_model.ImageRepresentation )[0]


def create_images_and_image_representations(
    submission: Submission,
    file_reference_uuid: str,
    result_summary: dict,
    persist_artefacts: Optional[bool] = False,
) -> List[bia_data_model.ImageRepresentation]:
    """Create image representation model instances and their actual images

    Create image representation model instances of the specified use
    types and the actual images for the use types and stage the images
    to S3.

    This function is only temporary whilst the API image conversion
    using the API is being developed and so it follows an inflexible
    convention of creating use types in the following order:
    UPLOADED_BY_SUBMITTER INTERACTIVE_DISPLAY STATIC_DISPLAY THUMBNAIL
    """

    representation_use_types = [
        use_type.value for use_type in ImageRepresentationUseType
    ]

    representations = {}
    for representation_use_type in representation_use_types:
        representations[representation_use_type] = create_image_representation(
            submission,
            [
                file_reference_uuid,
            ],
            representation_use_type=representation_use_type,
            result_summary=result_summary,
            persist_artefacts=True,
        )
    # Get image uploaded by submitter and update representation
    representation = representations["UPLOADED_BY_SUBMITTER"]
    # TODO file_uri of this representation = that of file reference(s)
    file_reference = get_bia_data_model_by_uuid(
        representation.original_file_reference_uuid[0],
        bia_data_model.FileReference,
        submission.accno,
    )
    local_path_to_uploaded_by_submitter_rep = stage_fileref_and_get_fpath(
        file_reference
    )

    # Convert to zarr, get zarr metadata
    representation = representations["INTERACTIVE_DISPLAY"]
    local_path_to_zarr = cached_convert_to_zarr_and_get_fpath(
        representation, local_path_to_uploaded_by_submitter_rep
    )
    pixel_metadata = image_utils.get_ome_zarr_pixel_metadata(local_path_to_zarr)

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
        image_utils.create_s3_uri_suffix_for_image_representation(
            submission.accno, representation
        ),
    )
    representation.file_uri = [
        file_uri,
    ]

    # Create thumbnail representation
    representation = representations["THUMBNAIL"]
    # TODO: This assumes zarr is multiscales image -> will not work for plate-well!!!
    thumbnail = generate_padded_thumbnail_from_ngff_uri(
        local_path_to_zarr / "0", dims=(256, 256)
    )
    local_path_to_thumbnail = image_utils.get_local_path_for_representation(
        representation.uuid, ".png"
    )
    with local_path_to_thumbnail.open("wb") as fh:
        thumbnail.save(fh)
    logger.info(f"Saved THUMBNAIL representation to {local_path_to_thumbnail}")
    representation.image_format = ".png"
    file_uri = copy_local_to_s3(
        local_path_to_thumbnail,
        image_utils.create_s3_uri_suffix_for_image_representation(
            submission.accno, representation
        ),
    )
    representation.file_uri = [
        file_uri,
    ]

    # Create static display (representative image) representation
    representation = representations["STATIC_DISPLAY"]
    static_display = generate_padded_thumbnail_from_ngff_uri(
        local_path_to_zarr / "0", dims=(512, 512)
    )
    local_path_to_static_display = image_utils.get_local_path_for_representation(
        representation.uuid, ".png"
    )
    with local_path_to_static_display.open("wb") as fh:
        static_display.save(fh)
    logger.info(
        f"Saved STATIC_DISPLAY representation to {local_path_to_static_display}"
    )
    representation.image_format = ".png"
    file_uri = copy_local_to_s3(
        local_path_to_static_display,
        image_utils.create_s3_uri_suffix_for_image_representation(
            submission.accno, representation
        ),
    )
    representation.file_uri = [
        file_uri,
    ]

    if persist_artefacts:
        persist(
            list(representations.values()),
            "image_representations",
            submission.accno,
        )

    return representations


def generate_image_representation_uuid(
    image_representation_dict: Dict[str, Any],
) -> str:
    attributes_to_consider = [
        "use_type",
        "original_file_reference_uuid",
        "representation_of_uuid",
    ]
    return dict_to_uuid(image_representation_dict, attributes_to_consider)
