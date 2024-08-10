import logging
from typing import List
from .utils import (
    dicts_to_api_models,
    find_sections_recursive,
    dict_to_uuid,
    persist,
    filter_model_dictionary,
    get_generic_section_as_list,
)
from ..biostudies import (
    Submission,
    attributes_to_dict,
)
from bia_shared_datamodels import bia_data_model, semantic_models

def get_specimen(submission: Submission) -> List[bia_data_model.Specimen]:

    associations = get_generic_section_as_list(
        section, ["Associations",], key_mapping
    )
    return associations
