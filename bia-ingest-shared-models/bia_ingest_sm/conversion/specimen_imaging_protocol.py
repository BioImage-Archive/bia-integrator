import logging
from typing import List, Any, Dict
from .utils import (
    dicts_to_api_models,
    find_sections_recursive,
    dict_to_uuid,
    persist
)
from ..biostudies import (
    Submission,
    attributes_to_dict,
)
from src.bia_models import bia_data_model

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_specimen_preparation_protocol(
    submission: Submission, persist_artefacts=False
) -> List[bia_data_model.Specimen]:

    specimen_preparation_protocol_model_dicts = extract_specimen_preparation_protocol_dicts(submission)
    specimen_preparation_protocols = dicts_to_api_models(specimen_preparation_protocol_model_dicts, bia_data_model.SpecimenPrepartionProtocol)

    if persist_artefacts and specimen_preparation_protocols:
        persist(specimen_preparation_protocols, "specimen_imaging_protocol", submission.accno)
    
    return specimen_preparation_protocols


def extract_specimen_preparation_protocol_dicts(submission: Submission) -> List[Dict[str, Any]]:
    specimen_sections = find_sections_recursive(submission.section, ["Specimen"], [])

    key_mapping = [
        ("title_id", "Title", ""),
        ("protocol_description", "Sample preparation protocol", ""),
    ]

    model_dicts = []
    for section in specimen_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}

        # Currently generates empty list as we need to change the submission template
        model_dict["signal_channel_information"] = []

        model_dict["accno"] = section.__dict__.get("accno", "")
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_specimen_preparation_uuid(model_dict)
        model_dicts.append(model_dict)

    return model_dicts


def generate_specimen_preparation_uuid(protocol_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
