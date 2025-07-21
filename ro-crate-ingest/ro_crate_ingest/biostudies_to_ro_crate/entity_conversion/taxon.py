import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
    Section,
)

from bia_shared_datamodels import ro_crate_models
import re

logger = logging.getLogger("__main__." + __name__)


TAXON_BNODE_INT = 0


def get_taxon_under_biosample(
    bio_sample_section: Section,
    unique_taxon_list: list[ro_crate_models.Taxon],
) -> ro_crate_models.Taxon:

    roc_object_list = []

    sections = find_sections_recursive(bio_sample_section, ["Organism"])

    if len(sections) > 0:
        for section in sections:
            tx_info: dict = get_taxon_information_from_section(section)
            taxon_id, is_unique = get_taxon_id_and_uniqueness(
                tx_info, unique_taxon_list
            )
            taxon = get_taxon(taxon_id, tx_info)
            roc_object_list.append(taxon)
            if is_unique:
                unique_taxon_list.append(taxon)

    else:
        tx_info: dict = get_taxon_information_from_biosample_attribute(
            bio_sample_section
        )
        taxon_id, is_unique = get_taxon_id_and_uniqueness(tx_info, unique_taxon_list)
        taxon = get_taxon(taxon_id, tx_info)
        roc_object_list.append(taxon)
        if is_unique:
            unique_taxon_list.append(taxon)

    return roc_object_list


def get_taxon_information_from_section(
    section: Section,
) -> dict:
    attr_dict = attributes_to_dict(section.attributes)

    info_dict = {
        "ncbiId": attr_dict.get("ncbi taxon id", None),
        "scientificName": attr_dict.get("scientific name", ""),
        "commonName": attr_dict.get("common name", ""),
    }

    return info_dict


def get_taxon_information_from_biosample_attribute(
    bio_sample_section: Section,
):
    bio_sample_attr_dict = attributes_to_dict(bio_sample_section.attributes)

    organism: str = bio_sample_attr_dict.get("organism", "")
    try:
        organism_scientific_name, organism_common_name = organism.split("(")
        organism_common_name = organism_common_name.rstrip(")")
    except ValueError:
        organism_scientific_name = organism
        organism_common_name = ""

    info_dict = {
        "ncbiId": None,
        "commonName": organism_common_name.strip(),
        "scientificName": organism_scientific_name.strip(),
    }

    return info_dict


def get_taxon(
    taxon_id: str,
    taxon_info: dict,
) -> ro_crate_models.Taxon:

    model_dict = {
        "@id": taxon_id,
        "@type": ["bia:Taxon"],
        "commonName": taxon_info["commonName"],
        "scientificName": taxon_info["scientificName"],
    }

    return ro_crate_models.Taxon(**model_dict)


def get_taxon_id_and_uniqueness(
    taxon_info: dict,
    unique_taxon_list: list[ro_crate_models.Taxon],
) -> tuple[str, bool]:
    taxon_id = None
    is_unique = True

    if taxon_info["ncbiId"]:
        taxon_id = re.sub("^[^0-9]*", "NCBI:txid", taxon_info["ncbiId"])
        for tx in unique_taxon_list:
            if tx.id == taxon_id:
                add_to_taxon_list = False

        return taxon_id, is_unique
    else:
        for tx in unique_taxon_list:
            if (
                tx.commonName == taxon_info["commonName"]
                and tx.scientificName == taxon_info["scientificName"]
            ):
                taxon_id = tx.id
                add_to_taxon_list = False
                return taxon_id, add_to_taxon_list

        global TAXON_BNODE_INT
        taxon_id = f"_:tx{TAXON_BNODE_INT}"
        TAXON_BNODE_INT += 1
        return taxon_id, is_unique
