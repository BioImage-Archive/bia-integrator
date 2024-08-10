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
from bia_shared_datamodels import bia_data_model, semantic_models

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_biosample(
    submission: Submission, persist_artefacts=False
) -> List[bia_data_model.BioSample]:

    biosample_model_dicts = extract_biosample_dicts(submission)
    biosamples = dicts_to_api_models(biosample_model_dicts, bia_data_model.BioSample)

    if persist_artefacts and biosamples:
        persist(biosamples, "biosamples", submission.accno)
    return biosamples


def extract_biosample_dicts(submission: Submission) -> List[Dict[str, Any]]:
    biosample_sections = find_sections_recursive(submission.section, ["Biosample"], [])

    key_mapping = [
        ("title_id", "Title", ""),
        ("biological_entity_description", "Biological entity", ""),
        ("organism", "Organism", ""),
    ]

    model_dicts = []
    for section in biosample_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}

        model_dict["accno"] = section.__dict__.get("accno", "")

        # Obtain scientic and common names from organism
        organism = model_dict.pop("organism", "")
        try:
            organism_scientific_name, organism_common_name = organism.split("(")
            organism_common_name = organism_common_name.rstrip(")")
        except ValueError:
            organism_scientific_name = organism
            organism_common_name = ""
        taxon = semantic_models.Taxon.model_validate(
            {
                "common_name": organism_common_name.strip(),
                "scientific_name": organism_scientific_name.strip(),
                "ncbi_id": None,
            }
        )
        model_dict["organism_classification"] = [taxon.model_dump()]

        # Populate intrinsic and extrinsic variables
        for api_key, biostudies_key in (
            ("intrinsic_variable_description", "Intrinsic variable"),
            ("extrinsic_variable_description", "Extrinsic variable",),
            ("experimental_variable_description", "Experimental variable",),
        ):
            model_dict[api_key] = []
            if biostudies_key in attr_dict:
                model_dict[api_key].append(attr_dict[biostudies_key])

        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_biosample_uuid(model_dict)
        model_dict["version"] = 1
        model_dict = filter_model_dictionary(model_dict, bia_data_model.BioSample)
        model_dicts.append(model_dict)

    return model_dicts

###############################################################
#
# Start of commented code block from experimental_imaging_dataset.py
# TODO: Need to persist this (API finally, but initially to disk)
#    biosamples_in_submission = biosample_conversion.get_biosample(submission)
#
#    # Index biosamples by title_id. Makes linking with associations more
#    # straight forward.
#    # Use for loop instead of dict comprehension to allow biosamples with
#    # same title to form list
#    biosamples_in_submission_uuid = {}
#    for biosample in biosample_conversion.get_biosample(
#        submission, persist_artefacts=persist_artefacts
#    ):
#        if biosample.title_id in biosamples_in_submission_uuid:
#            biosamples_in_submission_uuid[biosample.title_id].append(biosample.uuid)
#        else:
#            biosamples_in_submission_uuid[biosample.title_id] = [
#                biosample.uuid,
#            ]
#
#            # Biosample
#            biosamples_from_associations = [a.get("biosample") for a in associations]
#            for biosample in biosamples_from_associations:
#                if biosample in biosamples_in_submission_uuid:
#                    biosample_list.extend(biosamples_in_submission_uuid[biosample])
#
# End of commented code block from experimental_imaging_dataset.py
###############################################################


def generate_biosample_uuid(biosample_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "organism_classification",
        "biological_entity_description",
        "intrinsic_variable_description",
        "extrinsic_variable_description",
        "experimental_variable_description",
    ]
    return dict_to_uuid(biosample_dict, attributes_to_consider)
