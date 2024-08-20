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

logger = logging.getLogger('__main__.'+__name__)


def get_image_acquisition(
    submission: Submission, result_summary: dict, persist_artefacts=False
) -> List[bia_data_model.ImageAcquisition]:

    image_acquisition_model_dicts = extract_image_acquisition_dicts(submission)
    image_acquisitions = dicts_to_api_models(
        image_acquisition_model_dicts, bia_data_model.ImageAcquisition, result_summary[submission.accno]
    )

    if persist_artefacts and image_acquisitions:
        persist(image_acquisitions, "image_acquisitions", submission.accno)

    return image_acquisitions


def extract_image_acquisition_dicts(submission: Submission) -> List[Dict[str, Any]]:
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

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}

        if isinstance(model_dict["imaging_method_name"], str):
            model_dict["imaging_method_name"] = [model_dict["imaging_method_name"],]

        # TODO: change template / create logic to lookup the fbbi ID
        model_dict["fbbi_id"] = []

        model_dict["accno"] = section.__dict__.get("accno", "")
        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_image_acquisition_uuid(model_dict)
        model_dict["version"] = 1
        model_dict = filter_model_dictionary(
            model_dict, bia_data_model.ImageAcquisition
        )
        model_dicts.append(model_dict)

    logger.info(
        f"Ingesting: {submission.accno}. Created bia_data_model.ImageAcquisition. Count: {len(model_dicts)}"
    )
    return model_dicts


def generate_image_acquisition_uuid(protocol_dict: Dict[str, Any]) -> str:
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
