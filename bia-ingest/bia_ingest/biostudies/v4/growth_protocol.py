import logging
from typing import Any, Optional
from uuid import UUID

from bia_ingest.bia_object_creation_utils import dict_map_to_api_models
from bia_ingest.persistence_strategy import PersistenceStrategy

from bia_ingest.biostudies.submission_parsing_utils import (
    find_sections_recursive,
    attributes_to_dict,
    case_insensitive_get,
)
from bia_ingest.biostudies.api import Submission

from bia_shared_datamodels import bia_data_model
from bia_shared_datamodels.uuid_creation import create_protocol_uuid

logger = logging.getLogger("__main__." + __name__)


def get_growth_protocol_as_map(
    submission: Submission,
    study_uuid: UUID,
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
    specimen_growth_protocol_model_dicts = extract_growth_protocol_dicts(
        submission, study_uuid
    )
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
    study_uuid: UUID,
) -> dict[str, dict[str, Any]]:
    specimen_sections = find_sections_recursive(submission.section, ["Specimen"])

    key_mapping = [
        ("title", "Title", ""),
        ("protocol_description", "Growth protocol", ""),
    ]

    model_dict_map = {}
    for section in specimen_sections:
        attr_dict = attributes_to_dict(section.attributes)
        uuid_unique_input = section.accno if section.accno else ""

        if "Growth protocol" in attr_dict:
            model_dict = {
                k: case_insensitive_get(attr_dict, v, default)
                for k, v, default in key_mapping
            }

            model_dict["version"] = 0
            model_dict["uuid"] = create_protocol_uuid(study_uuid, uuid_unique_input)
            model_dict["object_creator"] = "bia_ingest"
            model_dict["additional_metadata"] = [
                {
                    "provenance": "bia_ingest",
                    "name": "uuid_unique_input",
                    "value": {"uuid_unique_input": uuid_unique_input},
                },
            ]

            model_dict_map[attr_dict["Title"] + ".growth_protocol"] = model_dict

    return model_dict_map
