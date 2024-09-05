import logging
from typing import List, Optional, Dict, Any
from uuid import UUID
from .utils import dict_to_uuid, get_bia_data_model_by_uuid
from ..image_utils import image_utils
from .experimentally_captured_image import get_experimentally_captured_image
from ..biostudies import (
    Submission,
)
from bia_shared_datamodels import bia_data_model
from bia_shared_datamodels.semantic_models import ImageRepresentationUseType


logger = logging.getLogger("__main__." + __name__)


def create_image_representation(
    submission: Submission,
    file_reference_uuids: List[UUID],
    representation_use_type: ImageRepresentationUseType,
    result_summary: dict,
    representation_location: Optional[str],
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
    )

    # TODO: Use bioformats or PIL for other formats (if on local disk)
    if representation_location:
        image_format = image_utils.get_image_extension(representation_location)
    else:
        image_format = ""

    pixel_metadata = {}
    total_size_in_bytes = 0
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

    model_dict = {
        "image_format": image_format,
        "use_type": representation_use_type,
        "file_uri": [],
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

    return bia_data_model.ImageRepresentation.model_validate(model_dict)
    # return dicts_to_api_models([model_dict,], bia_data_model.ImageRepresentation )[0]


def generate_image_representation_uuid(
    image_representation_dict: Dict[str, Any],
) -> str:
    attributes_to_consider = [
        "use_type",
        "original_file_reference_uuid",
        "representation_of_uuid",
    ]
    return dict_to_uuid(image_representation_dict, attributes_to_consider)
