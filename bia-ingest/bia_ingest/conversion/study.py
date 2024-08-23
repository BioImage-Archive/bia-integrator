import logging
from pathlib import Path
from pydantic import ValidationError
import re
from typing import List, Any, Dict
from .utils import (
    get_generic_section_as_dict,
    mattributes_to_dict,
    dict_to_uuid,
    find_sections_recursive,
    log_failed_model_creation,
)
from ..biostudies import (
    Submission,
    attributes_to_dict,
)
from ..config import settings
from bia_shared_datamodels import bia_data_model, semantic_models

logger = logging.getLogger("__main__." + __name__)


def get_study(
    submission: Submission, result_summary: dict, persist_artefacts: bool = False
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
        "version": 1,
    }
    # study_uuid = dict_to_uuid(study_dict, ["accession_id",])
    # study_dict["uuid"] = study_uuid
    try:
        study = bia_data_model.Study.model_validate(study_dict)
    except ValidationError:
        log_failed_model_creation(bia_data_model.Study, result_summary)

    if persist_artefacts:
        output_dir = Path(settings.bia_data_dir) / "studies"
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
            logger.info(f"Created {output_dir}")
        output_path = output_dir / f"{study.accession_id}.json"
        output_path.write_text(study.model_dump_json(indent=2))
        logger.info(f"Written {output_path}")
        # Save ALL file references
        # Save ALL biosamples
        # Save experimental_imaging_datasets
        # Save study
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
    submission: Submission, RESULT_SUMMARY: dict
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
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        return_list.append(
            semantic_models.External_reference.model_validate(model_dict)
        )
    return return_list


# TODO: Put comments and docstring
def get_grant(
    submission: Submission, RESULT_SUMMARY: dict
) -> List[semantic_models.Grant]:
    funding_body_dict = get_funding_body(submission, RESULT_SUMMARY)
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
        RESULT_SUMMARY[submission.accno],
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

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        try:
            affiliation_dict[section.accno] = (
                semantic_models.Affiliation.model_validate(model_dict)
            )
        except ValidationError:
            log_failed_model_creation(semantic_models.Affiliation, result_summary)

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

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        try:
            publications.append(semantic_models.Publication.model_validate(model_dict))
        except ValidationError:
            log_failed_model_creation(semantic_models.Publication, result_summary)

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
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
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
            log_failed_model_creation(semantic_models.Contributor, result_summary)

    return contributors
