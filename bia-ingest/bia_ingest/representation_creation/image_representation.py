import logging
from typing import List, Optional, Dict, Any
from pydantic import ValidationError
from uuid import UUID

from ..cli_logging import log_failed_model_creation, log_model_creation_count

from .utils import get_image_extension
from ..bia_object_creation_utils import (
    dict_to_uuid,
)

from .experimentally_captured_image import get_experimentally_captured_image
from ..ingest.biostudies import (
    Submission,
)
from bia_shared_datamodels import bia_data_model
from bia_shared_datamodels.semantic_models import ImageRepresentationUseType

from bia_ingest.persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)


def create_image_representation(
    submission: Submission,
    file_reference_uuids: List[UUID],
    representation_use_type: ImageRepresentationUseType,
    result_summary: dict,
    persister: PersistenceStrategy,
    representation_location: Optional[str] = None,
) -> bia_data_model.ImageRepresentation | None:
    """Create ImageRepresentation for specified FileReference(s)"""

    logger.debug(f"Fetching file reference with uuid(s) {file_reference_uuids}")
    try:
        file_references = persister.fetch_by_uuid(
            [str(uuid) for uuid in file_reference_uuids], bia_data_model.FileReference
        )
    except Exception as e:
        logger.error(
            f"Error fetching file references {file_reference_uuids}. Error was: {e}. Unable to create image representation and associated objects"
        )
        log_failed_model_creation(
            bia_data_model.ImageRepresentation, result_summary[submission.accno]
        )
        return
    # file_paths = [fr.file_path for fr in file_references]
    # if not any(
    #    [in_bioformats_single_file_formats_list(file_path) for file_path in file_paths]
    # ):
    #    message = f"Cannot process file references that do not have at least one entry in list of extensions bioformats can convert. File paths of fileReference(s) are: {file_paths}"
    #    raise Exception(message)

    experimentally_captured_image = get_experimentally_captured_image(
        submission=submission,
        dataset_uuid=file_references[0].submission_dataset_uuid,
        file_references=file_references,
        result_summary=result_summary,
        persister=persister,
    )
    if not experimentally_captured_image:
        logger.error(
            "Experimentally captured image not created. Cannot create image representations for file references {file_references}"
        )
        log_failed_model_creation(
            bia_data_model.ImageRepresentation, result_summary[submission.accno]
        )
        return

    image_format = ""
    pixel_metadata = {}
    total_size_in_bytes = 0
    file_uri = []

    if representation_use_type == ImageRepresentationUseType.UPLOADED_BY_SUBMITTER:
        if total_size_in_bytes == 0:
            total_size_in_bytes = sum([fr.size_in_bytes for fr in file_references])
        # TODO: Discuss what to do if file reference is list > 1 with different paths e.g. .hdr and .img for analyze. Currently just using first file reference
        if image_format == "":
            image_format = get_image_extension(file_references[0].file_path)
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
        "version": 0,
    }
    model_dict["uuid"] = generate_image_representation_uuid(model_dict)

    try:
        image_representation = bia_data_model.ImageRepresentation.model_validate(
            model_dict
        )
    except ValidationError:
        log_failed_model_creation(
            bia_data_model.ImageRepresentation,
            result_summary[submission.accno],
        )
        return

    persister.persist(
        [
            image_representation,
        ]
    )
    log_model_creation_count(
        bia_data_model.ImageRepresentation,
        1,
        result_summary[submission.accno],
    )
    return image_representation


def generate_image_representation_uuid(
    image_representation_dict: Dict[str, Any],
) -> str:
    attributes_to_consider = [
        "use_type",
        "original_file_reference_uuid",
        "representation_of_uuid",
    ]
    return dict_to_uuid(image_representation_dict, attributes_to_consider)
