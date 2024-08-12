import logging
from typing import Dict, List, Any
from .utils import (
    dicts_to_api_models,
    find_sections_recursive,
    dict_to_uuid,
    persist,
    filter_model_dictionary,
    get_generic_section_as_list,
    make_dict_from_objects,
)
from ..biostudies import (
    Submission,
    attributes_to_dict,
)
from . import (
    biosample as biosample_conversion,
    specimen_imaging_preparation_protocol as sipp_conversion,
    specimen_growth_protocol as sgp_conversion,
)
from bia_shared_datamodels import bia_data_model, semantic_models

def get_specimen(submission: Submission, persist_artefacts: bool = False) -> List[bia_data_model.Specimen]:
    """Create and persist bia_data_model.Specimen and models it depends on

    Create and persist the bia_data_model.Specimen and the models it 
    depends on - Biosample, (specimen) ImagePreparationProtocol, and
    (specimen) GrowthProtocol.
    """


    # ToDo - when API in operation do we attempt to retreive from
    # API first before creating biosample, specimen_growth_protocol and
    # specimen_preparation_protocol?

    # Biosamples
    biosamples = biosample_conversion.get_biosample(submission, persist_artefacts)

    # Index biosamples by title_id. Makes linking with associations more
    # straight forward.
    # Use for loop instead of dict comprehension to allow biosamples with
    # same title to form list
    biosample_uuids = make_dict_from_objects(biosamples, key_attr="title_id", value_attr="uuid")

    # ImagingPreparationProtocol
    imaging_preparation_protocols = sipp_conversion.get_specimen_imaging_preparation_protocol(submission, persist_artefacts)
    imaging_preparation_protocol_uuids = make_dict_from_objects(imaging_preparation_protocols, key_attr="title_id", value_attr="uuid")

    # GrowthProtocol
    growth_protocols = sgp_conversion.get_specimen_growth_protocol(submission, persist_artefacts)
    growth_protocol_uuids = make_dict_from_objects(growth_protocols, key_attr="title_id", value_attr="uuid")

    
    # ToDo - associations needed in multiple places -> create util func?
    key_mapping = [
        ("image_analysis", "Image analysis", None,),
        ("image_correlation", "Image correlation", None,),
        ("biosample", "Biosample", None,),
        ("image_acquisition", "Image acquisition", None,),
        ("specimen", "Specimen", None,),
    ]
    associations = get_generic_section_as_list(
        submission, ["Associations",], key_mapping
    )

    model_dicts = []
    for association in associations:
        biosample_titles = association.get("biosample")
        if type(biosample_titles) is not list:
            biosample_list = biosample_uuids[biosample_titles]
        else:
            biosample_list = []
            [biosample_list.extend(biosample_uuids[title]) for title in biosample_titles]
        
        specimen_titles = association.get("specimen")
        if type(specimen_titles) is not list:
            specimen_titles = [specimen_titles,]
        imaging_preparation_protocol_list = []
        [imaging_preparation_protocol_list.extend(imaging_preparation_protocol_uuids[title]) for title in specimen_titles];
        growth_protocol_list = []
        [growth_protocol_list.extend(growth_protocol_uuids[title]) for title in specimen_titles];

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
    return dicts_to_api_models(model_dicts, bia_data_model.Specimen)

def generate_specimen_uuid(specimen_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "imaging_preparation_protocol_uuid",
        "sample_of_uuid",
        "growth_protocol_uuid",
    ]
    return dict_to_uuid(specimen_dict, attributes_to_consider)
