import logging
from typing import List, Any, Dict, Optional

from ..bia_object_creation_utils import (
    dict_to_uuid,
    dicts_to_api_models,
    filter_model_dictionary,
)

from ..cli_logging import log_model_creation_count
from .biostudies.submission_parsing_utils import (
    find_sections_recursive,
    attributes_to_dict,
    case_insensitive_get,
)
from .biostudies.api import (
    Submission,
)
from bia_shared_datamodels import bia_data_model, semantic_models
from ..persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)


def get_biosample(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> List[bia_data_model.BioSample]:
    biosample_model_dicts = extract_biosample_dicts(submission)
    biosamples = dicts_to_api_models(
        biosample_model_dicts,
        bia_data_model.BioSample,
        result_summary[submission.accno],
    )

    log_model_creation_count(
        bia_data_model.BioSample, len(biosamples), result_summary[submission.accno]
    )

    if persister and biosamples:
        persister.persist(
            biosamples,
        )
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

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }

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
            (
                "extrinsic_variable_description",
                "Extrinsic variable",
            ),
            (
                "experimental_variable_description",
                "Experimental variable",
            ),
        ):
            model_dict[api_key] = []
            if biostudies_key in attr_dict:
                model_dict[api_key].append(attr_dict[biostudies_key])

        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_biosample_uuid(model_dict)
        model_dict["version"] = 0
        model_dict = filter_model_dictionary(model_dict, bia_data_model.BioSample)
        model_dicts.append(model_dict)

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
