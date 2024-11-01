import logging
from typing import List, Any, Dict, Optional

from .biostudies.submission_parsing_utils import attributes_to_dict

from ..bia_object_creation_utils import (
    dict_to_uuid,
    dicts_to_api_models,
    filter_model_dictionary,
)

from ..cli_logging import log_model_creation_count
from .biostudies.submission_parsing_utils import (
    find_sections_recursive,
    case_insensitive_get,
)
from .biostudies.api import (
    Submission,
)
from bia_shared_datamodels import bia_data_model
from ..persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)


def get_image_acquisition_protocol(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> List[bia_data_model.ImageAcquisitionProtocol]:
    image_acquisition_protocol_model_dicts = extract_image_acquisition_protocol_dicts(
        submission
    )
    image_acquisition_protocols = dicts_to_api_models(
        image_acquisition_protocol_model_dicts,
        bia_data_model.ImageAcquisitionProtocol,
        result_summary[submission.accno],
    )

    log_model_creation_count(
        bia_data_model.ImageAcquisitionProtocol,
        len(image_acquisition_protocols),
        result_summary[submission.accno],
    )

    if persister and image_acquisition_protocols:
        persister.persist(
            image_acquisition_protocols,
        )

    return image_acquisition_protocols


def extract_image_acquisition_protocol_dicts(
    submission: Submission,
) -> List[Dict[str, Any]]:
    acquisition_sections = find_sections_recursive(
        submission.section, ["Image acquisition"], []
    )

    key_mapping = [
        ("title_id", "Title", ""),
        ("protocol_description", "Image acquisition parameters", ""),
        ("imaging_instrument_description", "Imaging instrument", ""),
        ("imaging_method_name", "Imaging method", ""),
    ]

    model_dicts = []
    for section in acquisition_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }

        if isinstance(model_dict["imaging_method_name"], str):
            model_dict["imaging_method_name"] = [
                model_dict["imaging_method_name"],
            ]

        # TODO: change template / create logic to lookup the fbbi ID
        model_dict["fbbi_id"] = []

        model_dict["accno"] = section.__dict__.get("accno", "")
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_image_acquisition_protocol_uuid(model_dict)
        model_dict["version"] = 0
        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.ImageAcquisitionProtocol
        )
        model_dicts.append(model_dict)

    return model_dicts


def generate_image_acquisition_protocol_uuid(protocol_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
        "imaging_instrument_description",
        "imaging_method_name",
        "fbbi_id",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
