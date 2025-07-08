import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.api import (
    Submission,
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion.taxon import (
    get_taxon_under_biosample,
)
from typing import Optional

from bia_shared_datamodels import ro_crate_models

logger = logging.getLogger("__main__." + __name__)


def get_taxons_bio_samples_and_association_map(
    submission: Submission, roc_growth_protocols: dict[str, ro_crate_models.Protocol]
) -> tuple[
    list[ro_crate_models.Taxon],
    list[ro_crate_models.BioSample],
    dict[str, dict[Optional[str], str]],
]:

    biosample_sections = find_sections_recursive(submission.section, ["Biosample"], [])

    biosample_specimen_map = get_growth_protocols_for_biosample(
        submission, roc_growth_protocols
    )

    taxon_list = []
    roc_biosamples = []
    association_mapping = {}

    for section in biosample_sections:

        biosample_taxons = get_taxon_under_biosample(
            bio_sample_section=section,
            unique_taxon_list=taxon_list,
        )

        attr_dict = attributes_to_dict(section.attributes)

        for growth_protocol in biosample_specimen_map[attr_dict["title"]]:
            bio_sample = get_bio_sample(section, biosample_taxons, growth_protocol)
            roc_biosamples.append(bio_sample)

            if bio_sample.title not in association_mapping:
                association_mapping[bio_sample.title] = {}

            if growth_protocol:
                association_mapping[bio_sample.title][
                    growth_protocol.title
                ] = bio_sample.id
            else:
                association_mapping[bio_sample.title][None] = bio_sample.id

    return taxon_list, roc_biosamples, association_mapping


def get_bio_sample(
    section: Section,
    biosample_taxons: list[ro_crate_models.Taxon],
    growth_protocol: Optional[ro_crate_models.Protocol],
) -> ro_crate_models.BioSample:
    attr_dict = attributes_to_dict(section.attributes)

    model_dict = {
        "@id": (
            f"biostudies_bs:{section.accno}_{growth_protocol.id}"
            if growth_protocol
            else f"biostudies_bs:{section.accno}"
        ),
        "@type": ["bia:BioSample"],
        "title": attr_dict["title"],
        "biologicalEntityDescription": attr_dict.get("biological entity", ""),
        "intrinsicVariableDescription": get_value_in_list_or_empty_list(
            attr_dict, "intrinsic variable"
        ),
        "extrinsicVariableDescription": get_value_in_list_or_empty_list(
            attr_dict, "extrinsic variable"
        ),
        "experimentalVariableDescription": get_value_in_list_or_empty_list(
            attr_dict, "experimental variable"
        ),
        "organismClassification": [{"@id": taxon.id} for taxon in biosample_taxons],
        "growthProtocol": [{"@id": growth_protocol.id}] if growth_protocol else [],
    }

    return ro_crate_models.BioSample(**model_dict)


def get_value_in_list_or_empty_list(attr_dict: dict, field_name: str) -> list:
    value = attr_dict.get(field_name, None)
    if value:
        return [value]
    else:
        return []


def get_growth_protocols_for_biosample(
    submission: Submission, roc_growth_protocols: dict[str, ro_crate_models.Protocol]
) -> dict[str, list[ro_crate_models.Protocol | None]]:
    """
    Returns a map of the form:
    {
        "BioSample Title": [ "{Growth Protocol Object}", None]
    }
    Where the value in the list is either a Growth protocol object to be used with the BioSample, or None.
    """

    biosample_specimen_association = {}

    dataset_sections = find_sections_recursive(
        submission.section, ["Study Component"], []
    )
    for dataset_section in dataset_sections:
        associations = find_sections_recursive(dataset_section, ["Associations"], [])
        for association in associations:
            association_attributes = attributes_to_dict(association.attributes)

            biosample_title = association_attributes["biosample"]
            specimen_title = association_attributes["specimen"]

            if biosample_title not in biosample_specimen_association:
                biosample_specimen_association[biosample_title] = []

            growth_protocol = None
            if specimen_title in roc_growth_protocols:
                growth_protocol = roc_growth_protocols[specimen_title]

            if growth_protocol not in biosample_specimen_association[biosample_title]:
                biosample_specimen_association[biosample_title].append(growth_protocol)

    return biosample_specimen_association
