import logging
from typing import Dict, List, Any

from bia_shared_datamodels import bia_data_model, semantic_models

from .utils import (
    dicts_to_api_models,
    dict_to_uuid,
    persist,
    filter_model_dictionary,
    get_generic_section_as_list,
    object_value_pair_to_dict,
)
from ..biostudies import (
    Submission,
)
from . import (
    biosample as biosample_conversion,
    specimen_imaging_preparation_protocol as sipp_conversion,
    specimen_growth_protocol as sgp_conversion,
)

logger = logging.getLogger('biaingest')


def get_specimen(
    submission: Submission, result_summary: dict, persist_artefacts: bool = False
) -> List[bia_data_model.Specimen]:
    """Create and persist bia_data_model.Specimen and models it depends on

    Create and persist the bia_data_model.Specimen and the models it 
    depends on - Biosample, (specimen) ImagePreparationProtocol, and
    (specimen) GrowthProtocol.
    """

    logger.debug(
        f"Starting creation of bia_shared_models.Specimen models for submission: {submission.accno}"
    )
    # ToDo - when API in operation do we attempt to retreive from
    # API first before creating biosample, specimen_growth_protocol and
    # specimen_preparation_protocol?
    # Biosamples
    biosamples = biosample_conversion.get_biosample(submission, result_summary, persist_artefacts)

    # Index biosamples by title_id. Makes linking with associations more
    # straight forward.
    # Use for loop instead of dict comprehension to allow biosamples with
    # same title to form list
    biosample_uuids = object_value_pair_to_dict(
        biosamples, key_attr="title_id", value_attr="uuid"
    )

    # ImagingPreparationProtocol
    imaging_preparation_protocols = sipp_conversion.get_specimen_imaging_preparation_protocol(
        submission, result_summary, persist_artefacts
    )
    imaging_preparation_protocol_uuids = object_value_pair_to_dict(
        imaging_preparation_protocols, key_attr="title_id", value_attr="uuid"
    )

    # GrowthProtocol
    growth_protocols = sgp_conversion.get_specimen_growth_protocol(
        submission, result_summary, persist_artefacts
    )
    growth_protocol_uuids = object_value_pair_to_dict(
        growth_protocols, key_attr="title_id", value_attr="uuid"
    )

    # ToDo - associations needed in multiple places -> create util func?
    key_mapping = [
        ("biosample", "Biosample", None,),
        ("specimen", "Specimen", None,),
    ]
    associations = get_generic_section_as_list(
        submission, ["Associations",], key_mapping
    )

    model_dicts = []
    for association in associations:
        biosample_titles = association.get("biosample")
        if not isinstance(biosample_titles, list):
            biosample_list = biosample_uuids[biosample_titles]
        else:
            biosample_list = _extend_uuid_list(biosample_titles, biosample_uuids)

        specimen_titles = association.get("specimen")
        if not isinstance(specimen_titles, list):
            specimen_titles = [
                specimen_titles,
            ]
        imaging_preparation_protocol_list = _extend_uuid_list(
            specimen_titles, imaging_preparation_protocol_uuids
        )
        growth_protocol_list = _extend_uuid_list(specimen_titles, growth_protocol_uuids)

        model_dict = {
            "imaging_preparation_protocol_uuid": imaging_preparation_protocol_list,
            "sample_of_uuid": biosample_list,
            "growth_protocol_uuid": growth_protocol_list,
            "version": 1,
            "accession_id": submission.accno,
        }
        model_dict["uuid"] = generate_specimen_uuid(model_dict)

        model_dict = filter_model_dictionary(model_dict, bia_data_model.Specimen)
        model_dicts.append(model_dict)

    specimens = dicts_to_api_models(model_dicts, bia_data_model.Specimen, result_summary[submission.accno])

    if persist_artefacts and specimens:
        persist(specimens, "specimens", submission.accno)

    # ToDo: How should we deal with situation where specimens for a
    # submission are exactly the same? E.g. see associations of S-BIAD1287
    logger.info(
        f"Ingesting: {submission.accno}. Created bia_data_model.Specimen. Count: {len(model_dicts)}"
    )
    return specimens


def generate_specimen_uuid(specimen_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "imaging_preparation_protocol_uuid",
        "sample_of_uuid",
        "growth_protocol_uuid",
    ]
    return dict_to_uuid(specimen_dict, attributes_to_consider)


def _extend_uuid_list(titles, uuid_mapping):
    result = []
    for title in titles:
        result.extend(uuid_mapping[title])
    return result
