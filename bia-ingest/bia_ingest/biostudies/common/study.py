import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.package_specific_uuid_creation.shared import (
    create_study_uuid,
)
from email_validator import EmailNotValidError, validate_email
from pydantic import ValidationError

from bia_ingest.bia_object_creation_utils import dict_to_api_model, dicts_to_api_models
from bia_ingest.biostudies.api import Attribute, Submission
from bia_ingest.biostudies.common.constants import ALLOWED_LINK_TYPES, URL_TEMPLATES
from bia_ingest.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    case_insensitive_get,
    find_sections_recursive,
    mattributes_to_dict,
)
from bia_ingest.cli_logging import IngestionResult, log_failed_model_creation
from bia_ingest.persistence_strategy import PersistenceStrategy

# Strict URL detector for pre-checks (scheme://)
_URL_RE = re.compile(r"^[a-z][a-z0-9+.-]*://", re.I)

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
    grants = get_grant_and_funding_body(submission, result_summary)
    external_references = get_external_references(submission, result_summary)
    related_publications = get_related_publications(submission, result_summary)

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

    description = study_attributes.pop("Description", "")
    acknowledgement = study_attributes.pop("Acknowledgements", "")
    funding_statement = study_attributes.pop("Funding statement", "")
    # Put remaining attributes in bia_data_model.study.attribute
    additional_metadata = [
        {
            "provenance": semantic_models.Provenance.bia_ingest,
            "name": "Extras from biostudies.Submission.attributes",
            "value": {key: value},
        }
        for key, value in study_attributes.items()
    ]
    additional_metadata.append(
        {
            "provenance": semantic_models.Provenance.bia_ingest,
            "name": "biostudies json/pagetab entry",
            "value": {
                "json": f"https://www.ebi.ac.uk/biostudies/files/{submission.accno}/{submission.accno}.json",
                "pagetab": f"https://www.ebi.ac.uk/biostudies/files/{submission.accno}/{submission.accno}.tsv",
            },
        }
    )

    accno = getattr(submission, "accno")
    doi = submission_attributes.pop("DOI", None)
    release_date = submission_attributes.pop("ReleaseDate")

    # Note we have not been storing uuid_attribute in additional metedata since it's always just the accno.
    uuid, uuid_attribute = create_study_uuid(accno)

    study_dict = {
        "uuid": uuid,
        "accession_id": accno,
        "doi": doi,
        # TODO: Do more robust search for title - sometimes it is in
        #       actual submission - see old ingest code
        "title": study_title,
        "object_creator": semantic_models.Provenance.bia_ingest,
        "description": description,
        "release_date": release_date,
        "licence": licence,
        "acknowledgement": acknowledgement,
        "funding_statement": funding_statement,
        "keyword": keywords,
        "author": [contributor.model_dump() for contributor in contributors],
        "grant": [grant.model_dump() for grant in grants],
        "see_also": [
            external_reference.model_dump(mode="json")
            for external_reference in external_references
        ],
        "related_publication": [
            related_publication.model_dump(mode="json")
            for related_publication in related_publications
        ],
        "additional_metadata": additional_metadata,
        "version": 0,
    }

    study = dict_to_api_model(
        study_dict, bia_data_model.Study, result_summary[submission.accno]
    )

    if persister and study:
        persister.persist(
            [
                study,
            ]
        )
    if isinstance(study, bia_data_model.Study):  # Return study
        return study
    else:
        raise Exception("Failed to create study model")


def study_title_from_submission(submission: Submission) -> str:
    submission_attr_dict = attributes_to_dict(submission.attributes)
    study_section_attr_dict = attributes_to_dict(submission.section.attributes)

    study_title = submission_attr_dict.get("Title", None)
    if not study_title:
        study_title = study_section_attr_dict.get("Title", "Unknown")

    return study_title


def get_licence(study_attributes: Dict[str, Any]) -> semantic_models.Licence:
    """
    Return enum version of licence of study
    """
    temp = re.sub(r"\s", "_", study_attributes.get("License", "CC0"))
    licence = re.sub(r"\.", "", temp)
    licence = licence.replace("-", "_")
    return semantic_models.Licence[licence]


def normalise_link(link: str) -> str:
    # preserve "http://" or "https://"
    link = re.sub(r"^(https?:)//+", r"\1//", link)
    # collapse any other sequences of 3+ slashes to a single slash
    link = re.sub(r"(?<!:)/{3,}", "/", link)
    return link


def sanitise_link_and_link_type(link_raw, link_type_raw) -> Tuple[str, str]:
    # If link looks like a URL, keep as-is. AnyUrl will validate strictly later.
    """
    Sanitise a link and its type.

    If the link looks like a URL (validated by AnyUrl), keep as-is.
    If the link is not a URL, normalise the link_type and verify if provided.
    If link_type is not allowed, raise ValueError.
    If link is not a URL, try to build a URL using the template mapped from the display name.
    If no URL template is found for the link_type, raise ValueError.
    If the link is not a URL and no valid link_type templating is possible, raise ValueError.

    :param link_raw: The raw link string
    :param link_type_raw: The raw link type string
    :return: A tuple of the sanitised link and its type
    :rtype: Tuple[str, str]
    """
    link_raw = link_raw.strip().replace(" ", "")
    looks_like_a_link = isinstance(link_raw, str) and _URL_RE.match(link_raw)
    if looks_like_a_link:
        return link_raw, link_type_raw  # AnyUrl field will validate it

    # Normalize link_type and verify if provided
    lt_norm = None
    if link_type_raw is not None:
        lt_norm = str(link_type_raw).strip().lower()
        if lt_norm not in ALLOWED_LINK_TYPES and not looks_like_a_link:
            raise ValueError(f"link_type not allowed: {link_type_raw}.")

    # If link is not a URL
    if lt_norm is not None and link_raw is not None and isinstance(link_raw, str):
        # Try to build URL using template mapped from the display name
        template = URL_TEMPLATES.get(ALLOWED_LINK_TYPES[lt_norm].lower())
        if not template:
            raise ValueError(
                f"no URL template for link_type: {ALLOWED_LINK_TYPES[lt_norm]}."
            )
        link = template.format(link_raw.strip())

        return link, ALLOWED_LINK_TYPES[lt_norm]

    # If we reach here, link is not a URL and no valid link_type templating is possible
    raise ValueError(f"Invalid link or link_type provided: {link_raw}, {link_type_raw}")


def get_external_references(
    submission: Submission, result_summary: dict
) -> List[semantic_models.ExternalReference]:
    """
    Map biostudies.Submission.Link to semantic_models.ExternalReference
    """
    links = getattr(submission.section, "links")
    # For some studies links section is list of lists -flatten if necessary
    flattened_links = []
    for link_section in links:
        if isinstance(link_section, list):
            flattened_links.extend(link_section)
        else:
            flattened_links.append(link_section)
    external_references = list()
    for link_section in flattened_links:
        if hasattr(link_section, "attributes"):
            attributes_obj = getattr(link_section, "attributes")
        else:
            logger.warning(
                "get_external_references: No attributes found in link section."
            )
            continue
        attributes: dict = attributes_to_dict(attributes_obj)
        link, link_type = (
            getattr(link_section, "url"),
            case_insensitive_get(attributes, "type"),
        )
        if link is None:
            logger.warning("get_external_references: No link found in link section.")
            continue
        link_type = link_type.lower() if isinstance(link_type, str) else link_type
        logger.debug(
            f"get_external_references: before sanitise -> link: {link}, type: {link_type}"
        )
        link, link_type = sanitise_link_and_link_type(link, link_type)
        link = normalise_link(link)
        logger.debug(f"get_external_references: link: {link}, attributes: {attributes}")
        model_dict = {
            "link": link,
            "link_type": link_type,
            "description": case_insensitive_get(attributes, "description"),
        }

        external_reference = dict_to_api_model(
            model_dict,
            semantic_models.ExternalReference,
            result_summary[submission.accno],
        )
        if external_reference:
            external_references.append(external_reference)

    return external_references


# TODO: Put comments and docstring
def get_grant_and_funding_body(
    submission: Submission, result_summary: dict
) -> List[semantic_models.Grant]:
    funding_sections = find_sections_recursive(submission.section, ["Funding"])

    grant_list = []
    for section in funding_sections:
        attr = attributes_to_dict(section.attributes)

        funding_body = None
        if attr.get("Agency") is not None:
            funding_body_dict = {"display_name": attr["Agency"]}
            funding_body = dict_to_api_model(
                funding_body_dict,
                semantic_models.FundingBody,
                result_summary[submission.accno],
            )

        if attr.get("grant_id") is not None:
            grant_dict = {"id": attr["grant_id"]}
            if funding_body:
                grant_dict["funder"] = [funding_body]
            grant = dict_to_api_model(
                grant_dict, semantic_models.Grant, result_summary[submission.accno]
            )
            grant_list.append(grant)
        elif funding_body:
            logger.warning("Found funding body information but no grant")
    return grant_list


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
        ("address", "Address", None),
        ("website", "Website", None),
    ]

    affiliation_dict = {}
    for section in organisation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {
            k: case_insensitive_get(attr_dict, v, default)
            for k, v, default in key_mapping
        }

        affiliation = dict_to_api_model(
            model_dict, semantic_models.Affiliation, result_summary[submission.accno]
        )
        if affiliation:
            affiliation_dict[section.accno] = affiliation

    return affiliation_dict


def get_related_publications(
    submission: Submission, result_summary: dict
) -> List[semantic_models.Publication]:
    publication_sections = find_sections_recursive(
        submission.section,
        [
            "publication",
        ],
        [],
    )

    publications: list = list()
    for section in publication_sections:
        attributes: dict = attributes_to_dict(section.attributes)
        publication: dict = {
            k: case_insensitive_get(attributes, v, default)
            for k, v, default in [
                ("doi", "DOI", None),
                ("pubmed_id", "Pubmed ID", None),
                ("authors_name", "Authors", None),
                ("publication_year", "Year", None),
                ("title", "Title", None),
            ]
        }

        if publication["doi"] is not None:
            publication["doi"], _ = sanitise_link_and_link_type(
                publication["doi"], "doi"
            )
            logger.debug(f"get_related_publications: publication: {publication}")

        # Check all fields are not None because new ST allowed
        # some empty publications between August 2025 and October 2025
        if all(value is None for value in publication.values()):
            logger.warning("Skipping empty publication entry")
            continue
        try:
            publications.append(semantic_models.Publication.model_validate(publication))
        except ValidationError:
            log_failed_model_creation(
                semantic_models.Publication,
                result_summary[getattr(submission, "accno")],
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
        ("contact_email", "E-mail", None),
        ("orcid", "ORCID", None),
        ("affiliation", "affiliation", []),
    ]
    author_sections = find_sections_recursive(submission.section, ["author"])

    contributor_dicts = []
    email_warnings = []
    for section in author_sections:
        attributes = sanitise_affiliation_attribute(
            section.attributes, affiliation_dict, result_summary, submission.accno
        )
        attr_dict = mattributes_to_dict(attributes, affiliation_dict)
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

        sanitised_email, email_warnings = sanitise_contributor_email(
            model_dict["contact_email"], email_warnings
        )
        model_dict["contact_email"] = sanitised_email

        # Role may contain 'NoneType' object leading to AttributeError
        try:
            model_dict["role"] = [
                role.strip(" ") for role in attr_dict.get("Role", "").split(",")
            ]
        except AttributeError:
            model_dict["role"] = [""]

        contributor_dicts.append(model_dict)

    get_unique_email_warnings(email_warnings, result_summary, submission.accno)

    contributors = dicts_to_api_models(
        contributor_dicts, semantic_models.Contributor, result_summary[submission.accno]
    )

    return contributors


def sanitise_affiliation_attribute(
    attribute_list: List[Attribute],
    affiliation_dict: dict,
    result_summary: dict[str, IngestionResult],
    accno: str,
):
    sanitised_attribute_list = []
    for attribute in attribute_list:
        if attribute.name == "affiliation":
            affiliations_refs = [x.strip() for x in attribute.value.split(",")]
            for affiliation in affiliations_refs:
                if affiliation not in affiliation_dict.keys():
                    result_summary[accno].__setattr__(
                        "Uncaught_Exception",
                        str(result_summary[accno].Uncaught_Exception)
                        + f"Cannot find author's referenced affiliation: {affiliation};",
                    )
                else:
                    sanitised_attribute_list.append(
                        Attribute(name="affiliation", value=affiliation, reference=True)
                    )
        else:
            sanitised_attribute_list.append(attribute)
    return sanitised_attribute_list


def sanitise_contributor_email(email: str | None, email_warnings: list):
    if email is not None:
        try:
            email_info = validate_email(email, check_deliverability=False)
            email = email_info.normalized
        except EmailNotValidError as e:
            email_warnings.append(str(e))
            email = None

    return [email, email_warnings]


def get_unique_email_warnings(
    email_warnings: list, result_summary: dict[str, IngestionResult], accno: str
):
    if email_warnings != []:
        unique_warnings = list(set(email_warnings))
        for warning in unique_warnings:
            result_summary[accno].__setattr__(
                "Warning", "Skipped invalid author email: " + str(warning) + "\n"
            )
            logger.warning(f"Skipped invalid author email: {warning}")
