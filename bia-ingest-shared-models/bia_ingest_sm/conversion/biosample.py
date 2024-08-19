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

logger = logging.getLogger('biaingest')


def get_biosample(
    submission: Submission, result_summary: dict, persist_artefacts=False
) -> List[bia_data_model.BioSample]:

    biosample_model_dicts = extract_biosample_dicts(submission)
    biosamples = dicts_to_api_models(biosample_model_dicts, bia_data_model.BioSample, result_summary[submission.accno])

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


    logger.info(
        f"Ingesting: {submission.accno}. Created bia_data_model.BioSample. Count: {len(model_dicts)}"
    )

    return model_dicts


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
