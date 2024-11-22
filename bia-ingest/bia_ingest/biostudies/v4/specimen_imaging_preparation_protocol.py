import logging
from typing import Any, Optional

from ...bia_object_creation_utils import (
    dict_to_uuid,
    dict_map_to_api_models,
    filter_model_dictionary,
)

from ...cli_logging import log_model_creation_count
from ..submission_parsing_utils import (
    find_sections_recursive,
    attributes_to_dict,
    case_insensitive_get,
)
from ..api import (
    Submission,
)
from bia_shared_datamodels import bia_data_model
from ...persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)


def get_specimen_imaging_preparation_protocol_as_map(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> dict[str, bia_data_model.SpecimenImagingPreparationProtocol]:
    """
    Returns a dictionary of the form:

    {
      "Specimen Title": bia_data_model.SpecimenImagingPreparationProtocol(title_id: "Specimen Title", uuid:... )
    }

    The titles are what Biostudies uses in association objects to link study components to the relevant objects.
    """
    specimen_preparation_protocol_model_dicts = (
        extract_specimen_preparation_protocol_dicts(submission)
    )
    specimen_preparation_protocols = dict_map_to_api_models(
        specimen_preparation_protocol_model_dicts,
        bia_data_model.SpecimenImagingPreparationProtocol,
        result_summary[submission.accno],
    )

    log_model_creation_count(
        bia_data_model.SpecimenImagingPreparationProtocol,
        len(specimen_preparation_protocols),
        result_summary[submission.accno],
    )

    if persister and specimen_preparation_protocols:
        persister.persist(specimen_preparation_protocols)

    return specimen_preparation_protocols


def extract_specimen_preparation_protocol_dicts(
    submission: Submission,
) -> dict[str, dict[str, Any]]:
    specimen_sections = find_sections_recursive(submission.section, ["Specimen"])

    key_mapping = [
        ("title_id", "Title", ""),
        ("protocol_description", "Sample preparation protocol", ""),
    ]

    model_dict_map = {}
    for section in specimen_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }

        # Currently generates empty list as we need to change the submission template
        model_dict["signal_channel_information"] = []

        model_dict["accno"] = section.accno
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_specimen_imaging_preparation_uuid(model_dict)
        model_dict["version"] = 0
        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.SpecimenImagingPreparationProtocol
        )

        model_dict_map[attr_dict["Title"]] = model_dict

    return model_dict_map


def generate_specimen_imaging_preparation_uuid(protocol_dict: dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
