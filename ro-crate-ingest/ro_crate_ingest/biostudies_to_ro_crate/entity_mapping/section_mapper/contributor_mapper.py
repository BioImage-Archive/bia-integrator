import logging

from bia_ro_crate.models import ro_crate_models
from email_validator import validate_email

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
)

from .base_section_mapper import SectionMapper

logger = logging.getLogger("__main__." + __name__)


class ContributorMapper(SectionMapper):

    contributor_bnode_int: int
    section_type = "author"

    def __init__(self) -> None:
        self.contributor_bnode_int = 0
        super().__init__()

    def get_mapped_object(
        self, section: Section, association_map: dict[type, dict[str, str]]
    ):
        attributes_dict = attributes_to_dict(section.attributes)

        contributor_id = self.create_id(attributes_dict)

        contributor_dict = {
            "@type": ["Person", "bia:Contributor"],
            "@id": contributor_id,
            "displayName": attributes_dict["name"],
            "address": None,
            "website": None,
            "affiliation": self._get_affiliations(
                attributes_dict, association_map[ro_crate_models.Affiliaton]
            ),
            "role": self._get_roles(attributes_dict),
            "contactEmail": self._sanitise_contributor_email(
                attributes_dict.get("e-mail")
            ),
        }

        return ro_crate_models.Contributor(**contributor_dict)

    def create_id(self, attributes_dict: dict) -> str:
        orcid = attributes_dict.get("orcid")
        if orcid:
            id: str = orcid
            if not id.startswith("https://orcid.org/"):
                id = f"https://orcid.org/{id}"
        else:
            id = f"#c{self.contributor_bnode_int}"
            self.contributor_bnode_int += 1

        return id

    @staticmethod
    def _sanitise_contributor_email(email: str | None | list[str]) -> str | None:
        if email is not None and isinstance(email, str):
            email = email.strip().strip("<>")
            email_info = validate_email(email, check_deliverability=False)
            email = email_info.normalized
            return email

    @staticmethod
    def _get_roles(attributes_dict: dict[str, str | list[str]]):
        roles = attributes_dict.get("role") or []

        if isinstance(roles, str):
            roles = [role.strip(" ") for role in roles.split(",")]

        return roles

    @staticmethod
    def _get_affiliations(
        attributes_dict: dict,
        roc_affiliation_accno_id_map: dict[str, str],
    ):
        if "affiliation" not in attributes_dict:
            return []

        if isinstance(attributes_dict["affiliation"], str):
            attributes_dict["affiliation"] = [
                x.strip() for x in attributes_dict["affiliation"].split(",")
            ]

        return [
            {"@id": roc_affiliation_accno_id_map[x]}
            for x in attributes_dict["affiliation"]
        ]
