import logging
from typing import List, Any, Optional
from uuid import UUID
from copy import deepcopy

from bia_ingest.biostudies.generic_conversion_utils import (
    get_associations_for_section,
    Association,
)
from bia_ingest.biostudies.submission_parsing_utils import (
    find_sections_recursive,
    attributes_to_dict,
    case_insensitive_get,
)
from bia_ingest.biostudies.api import Submission, Section


from bia_ingest.bia_object_creation_utils import (
    dicts_to_api_models,
    dict_map_to_api_models,
)
from bia_ingest.cli_logging import IngestionResult
from bia_ingest.persistence_strategy import PersistenceStrategy


from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_bio_sample_uuid

logger = logging.getLogger("__main__." + __name__)


def get_bio_sample_as_map(
    submission: Submission,
    study_uuid: UUID,
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

    biosample_model_dicts = extract_biosample_dicts(
        submission, study_uuid, growth_protocol_map, result_summary
    )

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
    study_uuid: UUID,
    growth_protocol_map: dict[str, bia_data_model.BioSample],
    result_summary: dict,
) -> list[dict[str, Any]]:
    biosample_sections = find_sections_recursive(submission.section, ["Biosample"])

    key_mapping = [
        ("title", "Title", ""),
        ("biological_entity_description", "Biological entity", ""),
    ]

    model_dicts_map = {}
    for section in biosample_sections:
        attr_dict = attributes_to_dict(section.attributes)

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

        model_dict["organism_classification"] = [
            t.model_dump()
            for t in get_taxon(attr_dict, section, result_summary[submission.accno])
        ]

        bs_without_gp, growth_protocol_uuids = check_for_growth_protocol_uuids(
            attr_dict["Title"], submission, growth_protocol_map
        )
        model_dict["version"] = 0
        model_dict["object_creator"] = semantic_models.Provenance.bia_ingest

        for specimen, gp_uuid in growth_protocol_uuids:
            model_dict_with_gp = deepcopy(model_dict)
            model_dict_with_gp["growth_protocol_uuid"] = gp_uuid

            uuid_unique_input = f"{section.accno} {gp_uuid}"
            model_dict_with_gp["uuid"] = create_bio_sample_uuid(
                study_uuid,
                uuid_unique_input,
            )
            model_dict_with_gp["additional_metadata"] = [
                {
                    "provenance": semantic_models.Provenance.bia_ingest,
                    "name": "uuid_unique_input",
                    "value": {"uuid_unique_input": uuid_unique_input},
                },
            ]
            model_dicts_map[attr_dict["Title"] + "." + specimen] = model_dict_with_gp

        if bs_without_gp:
            model_dict["growth_protocol_uuid"] = None
            uuid_unique_input = f"{section.accno}"
            model_dict["uuid"] = create_bio_sample_uuid(
                study_uuid,
                uuid_unique_input,
            )
            model_dict["additional_metadata"] = [
                {
                    "provenance": semantic_models.Provenance.bia_ingest,
                    "name": "uuid_unique_input",
                    "value": {"uuid_unique_input": uuid_unique_input},
                },
            ]
            model_dicts_map[attr_dict["Title"]] = model_dict
    return model_dicts_map


def get_taxon(
    biosample_attr_dict: dict,
    biosample_section: Section,
    ingestion_result: IngestionResult,
) -> list[semantic_models.Taxon]:
    taxon_dicts = []

    subsection_organisms = find_sections_recursive(biosample_section, ["Organism"])
    if subsection_organisms:
        key_mapping = [
            ("common_name", "Common name", None),
            ("scientific_name", "Scientific name", None),
            ("ncbi_id", "NCBI taxon ID", None),
        ]
        for section in subsection_organisms:
            attr_dict = attributes_to_dict(section.attributes)

            model_dict = {
                k: case_insensitive_get(attr_dict, v, default)
                for k, v, default in key_mapping
            }

            taxon_dicts.append(model_dict)

    else:
        organism: str = biosample_attr_dict.pop("Organism", "")
        try:
            organism_scientific_name, organism_common_name = organism.split("(")
            organism_common_name = organism_common_name.rstrip(")")
        except ValueError:
            organism_scientific_name = organism
            organism_common_name = ""

        taxon_dicts.append(
            {
                "common_name": organism_common_name.strip(),
                "scientific_name": organism_scientific_name.strip(),
                "ncbi_id": None,
            }
        )

    taxon = dicts_to_api_models(taxon_dicts, semantic_models.Taxon, ingestion_result)

    return taxon


def check_for_growth_protocol_uuids(
    biosample_title: str,
    submission: Submission,
    growth_protocol_map: dict[str, bia_data_model.Protocol],
) -> tuple[bool, list[tuple[str, UUID]]]:
    # Get associations to allow mapping to biosample
    associations: List[Association] = [
        get_associations_for_section(section)[0]
        for section in find_sections_recursive(submission.section, ["Associations"], [])
    ]

    create_bio_sample_without_growth_protocol = False

    title_uuids = []
    for association in associations:
        # Check for non-growth protocol associations

        if (
            biosample_title == association.biosample
            and association.specimen + ".growth_protocol"
            not in growth_protocol_map.keys()
        ):
            create_bio_sample_without_growth_protocol = True

        # Check for associations with growth protocol (note not disjoint with non-growth protocol case)
        for gp_title in growth_protocol_map.keys():
            if (
                association.specimen + ".growth_protocol" == gp_title
                and biosample_title == association.biosample
            ):
                title_uuids.append(
                    (association.specimen, growth_protocol_map[gp_title].uuid)
                )

    return create_bio_sample_without_growth_protocol, title_uuids
