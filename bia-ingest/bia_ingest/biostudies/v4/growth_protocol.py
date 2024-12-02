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
from ...persistence_strategy import PersistenceStrategy
from bia_shared_datamodels import bia_data_model

logger = logging.getLogger("__main__." + __name__)


def get_growth_protocol_as_map(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> dict[str, bia_data_model.Protocol]:
    """
    Returns a dictionary of the form:

    {
      "Specimen Title.growth_protocol": bia_data_model.Protocol(title_id: "Specimen Title", uuid:... )
    }

    The titles are what Biostudies uses in association objects to link study components to the relevant objects.
    We append .growth_protocol to it since the specimen object is also used to create Specimen Imaging Preparation Protocols.
    """
    specimen_growth_protocol_model_dicts = extract_growth_protocol_dicts(submission)
    specimen_growth_protocols = dict_map_to_api_models(
        specimen_growth_protocol_model_dicts,
        bia_data_model.Protocol,
        result_summary[submission.accno],
    )

    if persister and specimen_growth_protocols:
        persister.persist(specimen_growth_protocols.values())

    return specimen_growth_protocols


def extract_growth_protocol_dicts(
    submission: Submission,
) -> dict[str, dict[str, Any]]:
    specimen_sections = find_sections_recursive(submission.section, ["Specimen"])

    key_mapping = [
        ("title_id", "Title", ""),
        ("protocol_description", "Growth protocol", ""),
    ]

    model_dict_map = {}
    for section in specimen_sections:
        attr_dict = attributes_to_dict(section.attributes)

        if "Growth protocol" in attr_dict:

            model_dict = {
                k: case_insensitive_get(attr_dict, v, default)
                for k, v, default in key_mapping
            }

            model_dict["accno"] = section.accno
            model_dict["accession_id"] = submission.accno
            model_dict["version"] = 0
            model_dict["uuid"] = generate_growth_protocol_uuid(model_dict)

            model_dict = filter_model_dictionary(model_dict, bia_data_model.Protocol)

            model_dict_map[attr_dict["Title"] + ".growth_protocol"] = model_dict

    return model_dict_map


def generate_growth_protocol_uuid(protocol_dict: dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
