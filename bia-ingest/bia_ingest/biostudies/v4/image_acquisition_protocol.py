import logging
from typing import List, Any, Dict, Optional

from bia_ingest.bia_object_creation_utils import (
    dict_to_uuid,
    dicts_to_api_models,
    dict_map_to_api_models,
    filter_model_dictionary,
)

from bia_ingest.cli_logging import log_model_creation_count
from bia_ingest.biostudies.submission_parsing_utils import (
    find_sections_recursive,
    case_insensitive_get,
    attributes_to_dict,
)
from bia_ingest.biostudies.api import Submission, Section
from bia_shared_datamodels import bia_data_model
from bia_ingest.persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)


# TODO: MAKE MAP
def get_image_acquisition_protocol_map(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> dict[str, bia_data_model.ImageAcquisitionProtocol]:
    """
    Returns a dictionary of the form:

    {
      "Image Acquisition Title": bia_data_model.ImageAcquisitionProtocol(title_id: "Image Acquisition Title", uuid:... )
    }

    The titles are what Biostudies uses in association objects to link study components to the relevant objects.
    """
    image_acquisition_protocol_model_dicts = extract_image_acquisition_protocol_dicts(
        submission
    )
    image_acquisition_protocols = dict_map_to_api_models(
        image_acquisition_protocol_model_dicts,
        bia_data_model.ImageAcquisitionProtocol,
        result_summary[submission.accno],
    )

    if persister and image_acquisition_protocols:
        persister.persist(
            image_acquisition_protocols.values(),
        )

    return image_acquisition_protocols


def extract_image_acquisition_protocol_dicts(
    submission: Submission,
) -> List[Dict[str, Any]]:
    acquisition_sections = find_sections_recursive(
        submission.section, ["Image acquisition"]
    )

    key_mapping = [
        ("title_id", "Title", ""),
        ("protocol_description", "Image acquisition parameters", ""),
        ("imaging_instrument_description", "Imaging instrument", ""),
        ("imaging_method_name", "Imaging method", None),
    ]

    model_dict_map = {}
    for section in acquisition_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }

        if not model_dict["imaging_method_name"]:
            model_dict["imaging_method_name"] = (
                get_imaging_method_names_from_subsection(section)
            )
        elif isinstance(model_dict["imaging_method_name"], str):
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
        model_dict_map[attr_dict["Title"]] = model_dict

    return model_dict_map


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


def get_imaging_method_names_from_subsection(
    image_acquisition_section: Section,
) -> list[str]:
    sections = find_sections_recursive(image_acquisition_section, ["Imaging Method"])
    imaging_method_name = []
    for section in sections:
        attr_dict = attributes_to_dict(section.attributes)
        if attr_dict["Ontology Name"] and attr_dict["Ontology Value"]:
            imaging_method_name.append(
                f"{attr_dict['Ontology Name']}:{attr_dict['Ontology Value']}"
            )
        elif attr_dict["Ontology Value"]:
            imaging_method_name.append(f"{attr_dict['Ontology Value']}")
    return imaging_method_name
