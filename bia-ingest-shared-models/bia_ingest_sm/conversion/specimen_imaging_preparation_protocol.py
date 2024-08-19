import logging
from typing import List, Any, Dict
from .utils import (
    dicts_to_api_models,
    find_sections_recursive,
    dict_to_uuid,
    persist,
    filter_model_dictionary,
)
from ..biostudies import (
    Submission,
    attributes_to_dict,
)
from bia_shared_datamodels import bia_data_model

logger = logging.getLogger('biaingest')


def get_specimen_imaging_preparation_protocol(
    submission: Submission, result_summary: dict, persist_artefacts=False
) -> List[bia_data_model.SpecimenImagingPreparationProtocol]:
    specimen_preparation_protocol_model_dicts = (
        extract_specimen_preparation_protocol_dicts(submission)
    )
    specimen_preparation_protocols = dicts_to_api_models(
        specimen_preparation_protocol_model_dicts,
        bia_data_model.SpecimenImagingPreparationProtocol,
        result_summary[submission.accno],
    )

    if persist_artefacts and specimen_preparation_protocols:
        persist(
            specimen_preparation_protocols,
            "specimen_imaging_protocols",
            submission.accno,
        )

    return specimen_preparation_protocols


def extract_specimen_preparation_protocol_dicts(
    submission: Submission,
) -> List[Dict[str, Any]]:
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
        model_dict["uuid"] = generate_specimen_imaging_preparation_uuid(model_dict)
        model_dict["version"] = 1
        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.SpecimenImagingPreparationProtocol
        )

        model_dicts.append(model_dict)
    
    logger.info(
        f"Ingesting: {submission.accno}. Created bia_data_model.SpecimenImagingPrepartionProtocol. Count: {len(model_dicts)}"
    )

    return model_dicts


def generate_specimen_imaging_preparation_uuid(protocol_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "protocol_description",
    ]
    return dict_to_uuid(protocol_dict, attributes_to_consider)
