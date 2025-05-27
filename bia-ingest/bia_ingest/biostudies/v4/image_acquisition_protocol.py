import logging
from typing import List, Any, Dict, Optional
from uuid import UUID

from bia_ingest.bia_object_creation_utils import dict_map_to_api_models
from bia_ingest.persistence_strategy import PersistenceStrategy

from bia_ingest.biostudies.submission_parsing_utils import (
    find_sections_recursive,
    case_insensitive_get,
    attributes_to_dict,
)
from bia_ingest.biostudies.api import Submission, Section

from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_image_acquisition_protocol_uuid

logger = logging.getLogger("__main__." + __name__)


# TODO: MAKE MAP
def get_image_acquisition_protocol_map(
    submission: Submission,
    study_uuid: UUID,
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
        submission, study_uuid
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
    study_uuid: UUID,
) -> List[Dict[str, Any]]:
    acquisition_sections = find_sections_recursive(
        submission.section, ["Image acquisition"]
    )

    key_mapping = [
        ("title", "Title", ""),
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

        # TODO: change template / create logic to lookup the fbbi ID
        model_dict["fbbi_id"] = []

        if not model_dict["imaging_method_name"]:
            # get imaging method name and fbbi_id from subsection if they exist
            # NOTE: this doesn't check the format of fbbi_id; it can be uri or id
            model_dict["imaging_method_name"], model_dict["fbbi_id"] = (
                get_imaging_method_fbbi_from_subsection(section)
            )
        elif isinstance(model_dict["imaging_method_name"], str):
            model_dict["imaging_method_name"] = [
                model_dict["imaging_method_name"],
            ]

        model_dict["version"] = 0
        uuid_unique_input = section.accno
        model_dict["uuid"] = create_image_acquisition_protocol_uuid(
            study_uuid,
            uuid_unique_input,
        )

        model_dict_map[attr_dict["Title"]] = model_dict

        model_dict["object_creator"] = semantic_models.Provenance.bia_ingest
        model_dict["additional_metadata"] = [
            {
                "provenance": semantic_models.Provenance.bia_ingest,
                "name": "uuid_unique_input",
                "value": {"uuid_unique_input": uuid_unique_input},
            },
        ]
    return model_dict_map


def get_imaging_method_fbbi_from_subsection(
    image_acquisition_section: Section,
) -> list:
    sections = find_sections_recursive(image_acquisition_section, ["Imaging Method"])
    imaging_method_name = []
    fbbi_id = []
    for section in sections:
        attr_dict = attributes_to_dict(section.attributes)
        if attr_dict.get("Ontology Term ID") and attr_dict.get("Ontology Value"):
            imaging_method_name.append(f"{attr_dict['Ontology Value']}")
            fbbi_id.append(f"{attr_dict['Ontology Term ID']}")
        elif attr_dict["Ontology Value"]:
            imaging_method_name.append(f"{attr_dict['Ontology Value']}")
    return [imaging_method_name, fbbi_id]
