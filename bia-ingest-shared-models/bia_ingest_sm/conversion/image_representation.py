import logging
from typing import List
from uuid import UUID
from .utils import dict_to_uuid, get_bia_data_model_by_uuid
from ..image_utils import image_utils
from .experimentally_captured_image import get_experimentally_captured_image
from ..biostudies import (
    Submission,
)
from bia_shared_datamodels import bia_data_model


logger = logging.getLogger("__main__." + __name__)


def image_representation_from_zarr(
    submission: Submission,
    file_reference_uuids: List[UUID],
    zarr_location: str,
    result_summary: dict,
) -> bia_data_model.ImageRepresentation:
    """Create ImageRepresentation for specified FileReference(s) and zarr"""

    # TODO: this should be replaced by API client and we would not need
    # accession_id
    file_references = [
        get_bia_data_model_by_uuid(uuid, bia_data_model.FileReference, submission.accno)
        for uuid in file_reference_uuids
    ]
    file_uris = [file_reference.uri for file_reference in file_references]
    experimentally_captured_image = get_experimentally_captured_image(
        submission=submission,
        dataset_uuid=file_references[0].submission_dataset_uuid,
        file_paths=[fr.file_path for fr in file_references],
        result_summary=result_summary,
    )

    pixel_metadata = image_utils.get_ome_zarr_pixel_metadata(zarr_location)

    model_dict = {
        "image_format": "",
        "use_type": "INTERACTIVE_DISPLAY",
        "file_uri": file_uris,
        "original_file_reference_uuid": file_reference_uuids,
        "representation_of_uuid": experimentally_captured_image.uuid,
        "total_size_in_bytes": image_utils.get_total_zarr_size(zarr_location),
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
    model_dict["uuid"] = dict_to_uuid(model_dict, list(model_dict.keys()))

    return bia_data_model.ImageRepresentation.model_validate(model_dict)
    # return dicts_to_api_models([model_dict,], bia_data_model.ImageRepresentation )[0]
