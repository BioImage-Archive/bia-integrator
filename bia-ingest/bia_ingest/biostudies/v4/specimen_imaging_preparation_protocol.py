import logging
from typing import Any, Optional
from uuid import UUID

from bia_ingest.bia_object_creation_utils import (
    dict_map_to_api_models,
)
from bia_ingest.persistence_strategy import PersistenceStrategy

from bia_ingest.biostudies.submission_parsing_utils import (
    find_sections_recursive,
    attributes_to_dict,
    case_insensitive_get,
)
from bia_ingest.biostudies.api import Submission

from bia_shared_datamodels import bia_data_model
from bia_shared_datamodels.uuid_creation import (
    create_specimen_imaging_preparation_protocol_uuid,
)

logger = logging.getLogger("__main__." + __name__)


def get_specimen_imaging_preparation_protocol_as_map(
    submission: Submission,
    study_uuid: UUID,
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
        extract_specimen_preparation_protocol_dicts(submission, study_uuid)
    )
    specimen_preparation_protocols = dict_map_to_api_models(
        specimen_preparation_protocol_model_dicts,
        bia_data_model.SpecimenImagingPreparationProtocol,
        result_summary[submission.accno],
    )

    if persister and specimen_preparation_protocols:
        persister.persist(specimen_preparation_protocols.values())

    return specimen_preparation_protocols


def extract_specimen_preparation_protocol_dicts(
    submission: Submission,
    study_uuid: UUID,
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

        model_dict["uuid"] = create_specimen_imaging_preparation_protocol_uuid(
            model_dict["title_id"], study_uuid
        )
        model_dict["version"] = 0

        model_dict_map[attr_dict["Title"]] = model_dict

    return model_dict_map
