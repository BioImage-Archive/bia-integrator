import logging
from typing import List, Any, Optional
from uuid import UUID
from bia_ingest.biostudies.generic_conversion_utils import (
    get_associations_for_section,
    Association,
)
from copy import deepcopy


from ...bia_object_creation_utils import (
    dict_to_uuid,
    dict_map_to_api_models,
    filter_model_dictionary,
)

from ...cli_logging import log_model_creation_count
from ..submission_parsing_utils import (
    find_sections_recursive,
    attributes_to_dict,
    case_insensitive_get,
)
from ..api import Submission, Section

from bia_shared_datamodels import bia_data_model, semantic_models
from ...persistence_strategy import PersistenceStrategy

logger = logging.getLogger("__main__." + __name__)


def get_bio_sample_as_map(
    submission: Submission,
    growth_protocol_map: dict[str, bia_data_model.Protocol],
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> dict[str, bia_data_model.BioSample]:
    """
    Returns a dictionary of the form:

    {
      "Biosample Title.Specimen Title": bia_data_model.BioSample(title_id: "Biosample Title", uuid:... )
    }

    The Keys will look like either: "Bio Sample Title.Specimen Title" or just "Bio Sample Title":
        - where "Bio Sample Title" is the user provided Title from Biostudies of the section
        - where "Specimen Title" is the user provided Title from Biostudies of the section
    The key will contain both Biosample and specimen title if a growth protocol of the biosample was created from the specimen

    These titles are what Biostudies uses in association objects to link study components to the relevant objects.
    """

    biosample_model_dicts = extract_biosample_dicts(submission, growth_protocol_map)

    biosamples = dict_map_to_api_models(
        biosample_model_dicts,
        bia_data_model.BioSample,
        result_summary[submission.accno],
    )

    if persister and biosamples:
        persister.persist(biosamples.values())

    return biosamples


def extract_biosample_dicts(
    submission: Submission,
    growth_protocol_map: dict[str, bia_data_model.BioSample],
) -> list[dict[str, Any]]:
    biosample_sections = find_sections_recursive(submission.section, ["Biosample"])

    key_mapping = [
        ("title_id", "Title", ""),
        ("biological_entity_description", "Biological entity", ""),
        ("organism", "Organism", ""),
    ]

    model_dicts_map = {}
    for section in biosample_sections:
        attr_dict = attributes_to_dict(section.attributes)

        for subsection in section.subsections:
            attr_dict |= attributes_to_dict(subsection.attributes)

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }

        # Populate intrinsic, extrinsic and experimental variables separately to base keys as they are list of strings
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

        model_dict["accno"] = section.accno
        model_dict["organism_classification"] = [
            get_taxon(model_dict, attr_dict).model_dump()
        ]
        model_dict["accession_id"] = submission.accno
        growth_protocol_uuids: list[tuple] = get_growth_protocol_title_uuids(
            attr_dict["Title"], submission, growth_protocol_map
        )
        model_dict["version"] = 0
        if len(growth_protocol_uuids) > 0:
            for gp_uuid in growth_protocol_uuids:
                model_dict_with_gp = deepcopy(model_dict)
                model_dict_with_gp["growth_protocol_uuid"] = gp_uuid[1]
                model_dict_with_gp["uuid"] = generate_biosample_uuid(model_dict_with_gp)
                model_dict_with_gp = filter_model_dictionary(
                    model_dict_with_gp, bia_data_model.BioSample
                )
                model_dicts_map[attr_dict["Title"] + "." + gp_uuid[0]] = (
                    model_dict_with_gp
                )
        else:
            model_dict["growth_protocol_uuid"] = None
            model_dict["uuid"] = generate_biosample_uuid(model_dict)
            model_dict = filter_model_dictionary(model_dict, bia_data_model.BioSample)
            model_dicts_map[attr_dict["Title"]] = model_dict
    return model_dicts_map


def generate_biosample_uuid(biosample_dict: dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "organism_classification",
        "biological_entity_description",
        "intrinsic_variable_description",
        "extrinsic_variable_description",
        "experimental_variable_description",
        "growth_protocol_uuid",
    ]
    return dict_to_uuid(biosample_dict, attributes_to_consider)


def get_taxon(model_dict: dict, attr_dict: dict) -> semantic_models.Taxon:
    organism = model_dict.pop("organism", "")
    try:
        organism_scientific_name, organism_common_name = organism.split("(")
        organism_common_name = organism_common_name.rstrip(")")
    except ValueError:
        organism_scientific_name = organism
        organism_common_name = ""
    taxon_key_mapping = [
        ("common_name", "Common name", organism_common_name.strip()),
        ("scientific_name", "Scientific name", organism_scientific_name.strip()),
        ("ncbi_id", "NCBI taxon ID", None),
    ]
    taxon_dict = {
        k: case_insensitive_get(attr_dict, v, default)
        for k, v, default in taxon_key_mapping
    }
    taxon = semantic_models.Taxon.model_validate(taxon_dict)
    return taxon


def get_growth_protocol_title_uuids(
    biosample_title: str,
    submission: Submission,
    growth_protocol_map: dict[str, bia_data_model.Protocol],
) -> list[tuple[str, UUID]]:

    # Get associations to allow mapping to biosample
    associations: List[Association] = [
        get_associations_for_section(section)[0]
        for section in find_sections_recursive(submission.section, ["Associations"], [])
    ]

    title_uuids = []
    for gp_title in growth_protocol_map.keys():
        for association in associations:
            if (
                gp_title.rstrip(".growth_protocol") == association.specimen
                and biosample_title == association.biosample
            ):
                title_uuids.append(
                    (association.specimen, growth_protocol_map[gp_title].uuid)
                )

    return title_uuids
