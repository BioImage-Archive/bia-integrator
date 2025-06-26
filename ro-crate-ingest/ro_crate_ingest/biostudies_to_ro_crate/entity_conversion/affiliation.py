import logging
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.api import (
    Submission,
    Section,
)

from bia_shared_datamodels import ro_crate_models


logger = logging.getLogger("__main__." + __name__)


def get_affiliations_by_accno(
    submission: Submission,
) -> dict[str, ro_crate_models.Affiliaton]:

    sections = find_sections_recursive(
        submission.section, ["organisation", "organization"], []
    )

    affiliation_dict = {}
    for section in sections:
        affiliation_dict[section.accno] = get_affiliation(section)
    return affiliation_dict


def get_affiliation(section: Section):

    attr_dict = attributes_to_dict(section.attributes)

    model_dict = {
        "@id": attr_dict.get("rorid", f"_:{section.accno}"),
        "@type": ["Organisation", "bia:Affiliation"],
        "displayName": attr_dict["name"],
        "website": attr_dict.get("website"),
        "address": attr_dict.get("address"),
    }

    return ro_crate_models.Affiliaton(**model_dict)
