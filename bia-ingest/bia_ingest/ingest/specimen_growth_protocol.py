import logging
from typing import List, Any, Dict, Optional


from ..bia_object_creation_utils import (
    dict_to_uuid,
    dicts_to_api_models,
    filter_model_dictionary,
)

from ..cli_logging import log_model_creation_count
from .biostudies.submission_parsing_utils import (
    find_sections_recursive,
    attributes_to_dict,
)
from .biostudies.api import (
    Submission,
)
from ..persistence_strategy import PersistenceStrategy
from bia_shared_datamodels import bia_data_model

logger = logging.getLogger("__main__." + __name__)


def get_specimen_growth_protocol(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> List[bia_data_model.SpecimenGrowthProtocol]:
    specimen_growth_protocol_model_dicts = extract_specimen_growth_protocol_dicts(
        submission
    )
    specimen_growth_protocols = dicts_to_api_models(
        specimen_growth_protocol_model_dicts,
        bia_data_model.SpecimenGrowthProtocol,
        result_summary[submission.accno],
    )

    log_model_creation_count(
        bia_data_model.SpecimenGrowthProtocol,
        len(specimen_growth_protocols),
        result_summary[submission.accno],
    )

    if persister and specimen_growth_protocols:
        persister.persist(specimen_growth_protocols)

    return specimen_growth_protocols


def extract_specimen_growth_protocol_dicts(
    submission: Submission,
) -> List[Dict[str, Any]]:
    specimen_sections = find_sections_recursive(submission.section, ["Specimen"], [])

    key_mapping = [
        ("title_id", "Title", ""),
        ("protocol_description", "Growth protocol", ""),
    ]

    model_dicts = []
    for section in specimen_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}

        model_dict["accno"] = section.__dict__.get("accno", "")
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_specimen_growth_protocol_uuid(model_dict)
        model_dict["version"] = 0
        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.SpecimenGrowthProtocol
        )

        model_dicts.append(model_dict)

    return model_dicts


def generate_specimen_growth_protocol_uuid(protocol_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)