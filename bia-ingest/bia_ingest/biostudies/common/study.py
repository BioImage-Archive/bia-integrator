import logging
from pydantic import ValidationError
import re
from typing import List, Any, Dict, Optional
from email_validator import validate_email, EmailNotValidError

from bia_ingest.cli_logging import (
    IngestionResult,
    log_failed_model_creation,
)
from bia_ingest.persistence_strategy import PersistenceStrategy
from bia_ingest.bia_object_creation_utils import (
    dict_to_api_model,
    dicts_to_api_models,
)

from bia_ingest.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    find_sections_recursive,
    mattributes_to_dict,
    case_insensitive_get,
)
from bia_ingest.biostudies.api import Attribute, Submission

from bia_shared_datamodels import bia_data_model, semantic_models
from bia_shared_datamodels.uuid_creation import create_study_uuid


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
            "provenance": semantic_models.Provenance("bia_ingest"),
            "name": "Extras from biostudies.Submission.attributes",
            "value": {key: value},
        }
        for key, value in study_attributes.items()
    ]
    additional_metadata.append(
        {
            "provenance": semantic_models.Provenance("bia_ingest"),
            "name": "biostudies json/pagetab entry",
            "value": {
                "json": f"https://www.ebi.ac.uk/biostudies/files/{submission.accno}/{submission.accno}.json",
                "pagetab": f"https://www.ebi.ac.uk/biostudies/files/{submission.accno}/{submission.accno}.tsv",
            },
        }
    )

    study_dict = {
        "uuid": create_study_uuid(submission.accno),
        "accession_id": submission.accno,
        # TODO: Do more robust search for title - sometimes it is in
        #       actual submission - see old ingest code
        "title": study_title,
        "object_creator": "bia_ingest",
        "description": description,
        "release_date": submission_attributes.pop("ReleaseDate"),
        "licence": licence,
        "acknowledgement": acknowledgement,
        "funding_statement": funding_statement,
        "keyword": keywords,
        "author": [c.model_dump() for c in contributors],
        "grant": [g.model_dump() for g in grants],
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
    return study


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
    return semantic_models.Licence[licence]


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

        external_ref = dict_to_api_model(
            model_dict,
            semantic_models.ExternalReference,
            result_summary[submission.accno],
        )
        if external_ref:
            return_list.append(external_ref)
    return return_list


# TODO: Put comments and docstring
def get_grant_and_funding_body(
    submission: Submission, result_summary: dict
) -> List[semantic_models.Grant]:
    funding_sections = find_sections_recursive(submission.section, ["Funding"])

    grant_list = []
    for section in funding_sections:
        attr = attributes_to_dict(section.attributes)

        funding_body = None
        if "Agency" in attr:
            funding_body_dict = {"display_name": attr["Agency"]}
            funding_body = dict_to_api_model(
                funding_body_dict,
                semantic_models.FundingBody,
                result_summary[submission.accno],
            )

        if "grant_id" in attr:
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

        affiliation = dict_to_api_model(
            model_dict, semantic_models.Affiliation, result_summary[submission.accno]
        )
        if affiliation:
            affiliation_dict[section.accno] = affiliation

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
        ("contact_email", "E-mail", None),
        ("role", "Role", None),
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
