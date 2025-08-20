import logging
from typing import Optional
from email_validator import validate_email
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Submission,
    Section,
)

from bia_shared_datamodels import ro_crate_models


logger = logging.getLogger("__main__." + __name__)



def get_contributors(
    submission: Submission,
    roc_affiliation_by_accno: dict[str, ro_crate_models.Affiliaton],
) -> list[ro_crate_models.Contributor]:

    global CONTRIBUTOR_BNODE_INT
    CONTRIBUTOR_BNODE_INT = 0

    sections = find_sections_recursive(submission.section, ["author"])

    contributors = []
    for section in sections:

        contributors.append(get_contributor(section, roc_affiliation_by_accno))

    return contributors


def get_contributor(
    section: Section,
    roc_affiliation_by_accno: dict[str, ro_crate_models.Affiliaton],
) -> ro_crate_models.Contributor:

    attributes_dict = attributes_to_dict(section.attributes)

    contributor_dict = {
        "@type": ["Person", "bia:Contributor"],
        "@id": get_contributor_id(attributes_dict),
        "displayName": attributes_dict["name"],
        "address": None,
        "website": None,
        "affiliation": get_affiliaitons(attributes_dict, roc_affiliation_by_accno),
        "role": get_roles(attributes_dict),
        "contactEmail": sanitise_contributor_email(attributes_dict.get("e-mail")),
    }
    return ro_crate_models.Contributor(**contributor_dict)


def get_contributor_id(attributes_dict: dict):

    if "orcid" in attributes_dict:
        id: str = attributes_dict["orcid"]
        if not id.startswith("https://orcid.org/"):
            id = f"https://orcid.org/{id}"
    else:
        global CONTRIBUTOR_BNODE_INT
        id = f"_:c{CONTRIBUTOR_BNODE_INT}"
        CONTRIBUTOR_BNODE_INT += 1

    return id


def sanitise_contributor_email(email: Optional[str]):
    if email is not None:
        email_info = validate_email(email, check_deliverability=False)
        email = email_info.normalized
    return email


def get_roles(attributes_dict: dict):
    roles = []
    if "role" in attributes_dict:
        if isinstance(attributes_dict["role"], list):
            roles = attributes_dict["role"]
        else:
            roles = [
                role.strip(" ") for role in attributes_dict.get("role", "").split(",")
            ]

    return roles


def get_affiliaitons(
    attributes_dict: dict,
    roc_affiliation_by_accno: dict[str, ro_crate_models.Affiliaton],
):

    if "affiliation" not in attributes_dict:
        return []

    if isinstance(attributes_dict["affiliation"], str):
        attributes_dict["affiliation"] = [
            x.strip() for x in attributes_dict["affiliation"].split(",")
        ]

    return [
        {"@id": roc_affiliation_by_accno[x].id} for x in attributes_dict["affiliation"]
    ]
