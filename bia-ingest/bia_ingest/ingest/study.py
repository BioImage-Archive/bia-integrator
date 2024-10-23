import logging
from pydantic import ValidationError
import re
from typing import List, Any, Dict, Optional

from .biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
    mattributes_to_dict,
    case_insensitive_get,
)

from ..bia_object_creation_utils import dict_to_uuid

from ..cli_logging import log_failed_model_creation
from .generic_conversion_utils import (
    get_generic_section_as_dict,
)
from .biostudies.api import (
    Submission,
)
from ..persistence_strategy import PersistenceStrategy
from bia_shared_datamodels import bia_data_model, semantic_models

logger = logging.getLogger("__main__." + __name__)


def get_study(
    submission: Submission,
    result_summary: dict,
    persister: Optional[PersistenceStrategy] = None,
) -> bia_data_model.Study:
    """
    Return an API study model populated from the submission
    """

    submission_attributes = attributes_to_dict(submission.attributes)
    contributors = get_contributor(submission, result_summary)
    grants = get_grant(submission, result_summary)

    study_attributes = attributes_to_dict(submission.section.attributes)

    study_title = study_title_from_submission(submission)
    if "Title" in study_attributes:
        study_attributes.pop("Title")

    licence = get_licence(study_attributes)
    if "License" in study_attributes:
        study_attributes.pop("License")

    keywords = study_attributes.get("Keywords", [])
    if not isinstance(keywords, list):
        keywords = [
            keywords,
        ]
    if "Keywords" in study_attributes:
        study_attributes.pop("Keywords")

    study_dict = {
        "uuid": get_study_uuid(submission),
        "accession_id": submission.accno,
        # TODO: Do more robust search for title - sometimes it is in
        #       actual submission - see old ingest code
        "title": study_title,
        "description": study_attributes.pop("Description", None),
        "release_date": submission_attributes.pop("ReleaseDate"),
        "licence": licence,
        "acknowledgement": study_attributes.pop("Acknowledgements", None),
        "funding_statement": study_attributes.pop("Funding statement", None),
        "keyword": keywords,
        "author": [c.model_dump() for c in contributors],
        "grant": [g.model_dump() for g in grants],
        "attribute": study_attributes,
        "version": 0,
    }
    try:
        study = bia_data_model.Study.model_validate(study_dict)
    except ValidationError:
        log_failed_model_creation(
            bia_data_model.Study, result_summary[submission.accno]
        )

    if persister:
        persister.persist(
            [
                study,
            ]
        )
    return study


def get_study_uuid(submission: Submission) -> str:
    return dict_to_uuid(
        {"accession_id": submission.accno},
        [
            "accession_id",
        ],
    )


def study_title_from_submission(submission: Submission) -> str:
    submission_attr_dict = attributes_to_dict(submission.attributes)
    study_section_attr_dict = attributes_to_dict(submission.section.attributes)

    study_title = submission_attr_dict.get("Title", None)
    if not study_title:
        study_title = study_section_attr_dict.get("Title", "Unknown")

    return study_title


def get_licence(study_attributes: Dict[str, Any]) -> semantic_models.LicenceType:
    """
    Return enum version of licence of study
    """
    licence = re.sub(r"\s", "_", study_attributes.get("License", "CC0"))
    return semantic_models.LicenceType(licence)


def get_external_reference(
    submission: Submission, result_summary: dict
) -> List[semantic_models.ExternalReference]:
    """
    Map biostudies.Submission.Link to semantic_models.ExternalReference
    """
    sections = find_sections_recursive(
        submission.section,
        [
            "links",
        ],
        [],
    )

    key_mapping = [
        ("link", "url", None),
        ("link_type", "Type", None),
        ("description", "Description", None),
    ]

    return_list = []
    for section in sections:
        attr_dict = attributes_to_dict(section.attributes)
        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }
        try:
            return_list.append(
                semantic_models.ExternalReference.model_validate(model_dict)
            )
        except ValidationError:
            log_failed_model_creation(
                semantic_models.ExternalReference, result_summary[submission.accno]
            )
    return return_list


# TODO: Put comments and docstring
def get_grant(
    submission: Submission, result_summary: dict
) -> List[semantic_models.Grant]:
    funding_body_dict = get_funding_body(submission, result_summary)
    key_mapping = [
        ("id", "grant_id", None),
    ]
    grant_dict = get_generic_section_as_dict(
        submission,
        [
            "Funding",
        ],
        key_mapping,
        semantic_models.Grant,
        result_summary[submission.accno],
    )

    grant_list = []
    for k, v in grant_dict.items():
        if k in funding_body_dict:
            v.funder.append(funding_body_dict[k])
        grant_list.append(v)
    return grant_list


# TODO: Put comments and docstring
def get_funding_body(
    submission: Submission, result_summary: dict
) -> semantic_models.FundingBody:
    key_mapping = [
        (
            "display_name",
            "Agency",
            None,
        ),
    ]
    funding_body = get_generic_section_as_dict(
        submission,
        [
            "Funding",
        ],
        key_mapping,
        semantic_models.FundingBody,
        result_summary[submission.accno],
    )
    return funding_body


def get_affiliation(
    submission: Submission, result_summary: dict
) -> Dict[str, semantic_models.Affiliation]:
    """
    Maps biostudies.Submission.Organisation sections to semantic_models.Affiliations
    """

    organisation_sections = find_sections_recursive(
        submission.section, ["organisation", "organization"], []
    )

    key_mapping = [
        ("display_name", "Name", None),
        ("rorid", "RORID", None),
        # TODO: Address does not exist in current biostudies.Organisation
        ("address", "Address", None),
        # TODO:  does not exist in current biostudies.Organisation
        ("website", "Website", None),
    ]

    affiliation_dict = {}
    for section in organisation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }
        try:
            affiliation_dict[section.accno] = (
                semantic_models.Affiliation.model_validate(model_dict)
            )
        except ValidationError:
            log_failed_model_creation(
                semantic_models.Affiliation, result_summary[submission.accno]
            )

    return affiliation_dict


def get_publication(
    submission: Submission, result_summary: dict
) -> List[semantic_models.Publication]:
    publication_sections = find_sections_recursive(
        submission.section,
        [
            "publication",
        ],
        [],
    )
    key_mapping = [
        ("doi", "DOI", None),
        ("pubmed_id", "Pubmed ID", None),
        ("author", "Authors", None),
        ("release_date", "Year", None),
        ("title", "Title", None),
    ]
    publications = []
    for section in publication_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }
        try:
            publications.append(semantic_models.Publication.model_validate(model_dict))
        except ValidationError:
            log_failed_model_creation(
                semantic_models.Publication, result_summary[submission.accno]
            )

    return publications


def get_contributor(
    submission: Submission, result_summary: dict
) -> List[semantic_models.Contributor]:
    """
    Map authors in submission to semantic_model.Contributors
    """
    affiliation_dict = get_affiliation(submission, result_summary)
    key_mapping = [
        ("display_name", "Name", None),
        ("contact_email", "E-mail", "not@supplied.com"),
        ("role", "Role", None),
        ("orcid", "ORCID", None),
        ("affiliation", "affiliation", []),
    ]
    author_sections = find_sections_recursive(
        submission.section,
        [
            "author",
        ],
        [],
    )
    contributors = []
    for section in author_sections:
        attr_dict = mattributes_to_dict(section.attributes, affiliation_dict)
        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }
        # TODO: Find out if authors can have more than one organisation ->
        #       what are the implications for mattributes_to_dict?
        if model_dict["affiliation"] is None:
            model_dict["affiliation"] = []
        elif not isinstance(model_dict["affiliation"], list):
            model_dict["affiliation"] = [
                model_dict["affiliation"],
            ]
        try:
            contributors.append(semantic_models.Contributor.model_validate(model_dict))
        except ValidationError:
            log_failed_model_creation(
                semantic_models.Contributor, result_summary[submission.accno]
            )

    return contributors
