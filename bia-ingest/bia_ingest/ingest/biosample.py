import logging
from typing import List, Any, Dict, Optional

from bia_ingest.ingest.generic_conversion_utils import get_associations_for_section
from bia_ingest.ingest.specimen_growth_protocol import (
    get_specimen_growth_protocol,
)

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

# from bia_ingest.ingest.specimen_growth_protocol import get_specimen_growth_protocol
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


# TODO: Rewrite this function. What we need is
# get_biosample_for_association https://app.clickup.com/t/8696nan92
def get_biosample_by_study_component(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> Dict[str, bia_data_model.BioSample]:
    """Return biosample associated with growth protocol for s.component

    Return a dict with study component title as key and biosample as
    value. The biosample will be associated with the growth protocol
    for the study component if one exists.
    """

    biosample_model_dicts = extract_biosample_dicts(submission, filter_dict=False)

    # Get growth protocols as UUIDs needed in biosample
    # If we are persisting this call ensures the growth protocols
    # are created and persisted.
    growth_protocols = get_specimen_growth_protocol(
        submission, result_summary, persister
    )
    growth_protocol_title_to_uuid_map = {
        gp.title_id: gp.uuid for gp in growth_protocols
    }

    # Get associations to allow mapping to biosample
    study_components = find_sections_recursive(
        submission.section,
        [
            "Study Component",
        ],
        [],
    )

    biosample_by_study_component = {}
    for study_component in study_components:
        study_component_name = next(
            attr.value for attr in study_component.attributes if attr.name == "Name"
        )
        if study_component_name not in biosample_by_study_component:
            biosample_by_study_component[study_component_name] = []
        associations = get_associations_for_section(study_component)
        for association in associations:
            biosample_title = association.get("biosample", None)
            specimen_title = association.get("specimen", None)
            growth_protocol_uuid = None
            if biosample_title and specimen_title:
                growth_protocol_uuid = growth_protocol_title_to_uuid_map.get(
                    specimen_title, None
                )
            elif biosample_title:
                logger.warning(
                    f"Could not find specimen association for biosample {biosample_title} in study component {study_component_name}"
                )
            else:
                # This is to be expected in some cases. E.g. Annotation datasets ...
                logger.warning(
                    f"Could not find biosample for study component {study_component_name}"
                )
                continue

            # Attach specimen growth protocol uuid and recompute biosample uuid
            # Currently assuming there should be only one growth protocol
            # per biosample AND biosample titles are unique
            # TODO: Log warning if above is not true.
            biosample_model_dict = next(
                model_dict
                for model_dict in biosample_model_dicts
                if model_dict["title_id"] == biosample_title
            )
            if growth_protocol_uuid:
                biosample_model_dict["growth_protocol_uuid"] = growth_protocol_uuid
                biosample_model_dict["uuid"] = generate_biosample_uuid(
                    biosample_model_dict
                )
            biosample_model_dict = filter_model_dictionary(
                biosample_model_dict, bia_data_model.BioSample
            )
            biosample_model = dicts_to_api_models(
                [
                    biosample_model_dict,
                ],
                bia_data_model.BioSample,
                result_summary[submission.accno],
            )
            biosample_by_study_component[study_component_name].append(
                biosample_model[0]
            )

    # Save unique biosample models
    biosamples = {}
    for biosample_list in biosample_by_study_component.values():
        biosamples |= {biosample.uuid: biosample for biosample in biosample_list}
    biosamples = list(biosamples.values())
    if persister and biosamples:
        persister.persist(biosamples)
        log_model_creation_count(
            bia_data_model.BioSample, len(biosamples), result_summary[submission.accno]
        )
    return biosample_by_study_component


def extract_biosample_dicts(
    submission: Submission,
    filter_dict: bool = True,
) -> List[Dict[str, Any]]:
    biosample_sections = find_sections_recursive(submission.section, ["Biosample"], [])

    key_mapping = [
        ("title_id", "Title", ""),
        ("biological_entity_description", "Biological entity", ""),
        ("organism", "Organism", ""),
    ]

    model_dicts = []
    for section in biosample_sections:
        attr_dict = attributes_to_dict(section.attributes)
        for subsection in section.subsections:
            attr_dict |= attributes_to_dict(subsection.attributes)

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
        model_dict["growth_protocol_uuid"] = None
        model_dict["uuid"] = generate_biosample_uuid(model_dict)
        model_dict["version"] = 0
        if filter_dict:
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
        "growth_protocol_uuid",
    ]
    return dict_to_uuid(biosample_dict, attributes_to_consider)
