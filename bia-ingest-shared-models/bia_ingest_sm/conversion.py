import hashlib
import uuid
from typing import List, Any, Dict, Optional, Tuple
from .biostudies import Submission, attributes_to_dict, Section, Attribute
from src.bia_models import bia_data_model, semantic_models

def get_study(submission: Submission) -> bia_data_model.Study:
    """Return an API study model populated from the submission

    """
    
    submission_attributes = attributes_to_dict(submission.attributes)
    contributors = get_contributor(submission)
    grants = get_grant(submission)

    study_attributes = attributes_to_dict(submission.section.attributes)

    study_dict = {
        "accession_id": submission.accno,
        # TODO: Do more robust search for title - sometimes it is in
        #       actual submission - see old ingest code
        "title": study_attributes.pop("Title", None),
        "description": study_attributes.pop("Description", None),
        "release_date": submission_attributes.pop("ReleaseDate"),
        "licence": get_licence(study_attributes),
        "acknowledgement": study_attributes.pop("Acknowledgements", None),
        "funding_statement": study_attributes.pop("Funding statement", None),
        "keyword": study_attributes.pop("Keywords", []),
        "author": [c.model_dump() for c in contributors],
        "grant": [g.model_dump() for g in grants],
        "attribute": study_attributes,
        "experimental_imaging_component": [],
        "annotation_component": [],

    }
    study_uuid = dict_to_uuid(study_dict, ["accession_id", "title", "release_date",])
    study_dict["uuid"] = study_uuid
    study = bia_data_model.Study.model_validate(study_dict)

    return study

def get_licence(submission_attributes: Dict[str, Any]) -> semantic_models.LicenceType:
    """Return enum version of licence of study

    """
    licence = submission_attributes.pop("License").replace(" ", "_")
    return semantic_models.LicenceType(licence)

def get_external_reference(submission: Submission) -> List[semantic_models.ExternalReference]:
    """Map biostudies.Submission.Link to semantic_models.ExternalReference

    """
    sections = find_sections_recursive(
        submission.section, ["links",]
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
        return_list.append(semantic_models.External_reference.model_validate(model_dict))
    return return_list

# TODO: Put comments and docstring
def get_grant(submission: Submission) -> List[semantic_models.Grant]:
    funding_body_dict = get_funding_body(submission)
    key_mapping = [
        ("id", "grant_id", None),
    ]
    grant_dict = get_generic_section_as_dict(submission, ["Funding",], semantic_models.Grant, key_mapping)

    grant_list = []
    for k, v in grant_dict.items():
        if k in funding_body_dict:
            v.funder.append(funding_body_dict[k])
        grant_list.append(v)
    return grant_list
    
# TODO: Put comments and docstring
def get_funding_body(submission: Submission) -> semantic_models.FundingBody:
    
    key_mapping = [
        ("display_name", "Agency", None,),
    ]
    funding_body = get_generic_section_as_dict(submission, ["Funding",], semantic_models.FundingBody, key_mapping)
    return funding_body


# TODO: Put comments and docstring
def get_generic_section_as_list(submission: Submission, section_name: List[str], mapped_object: [Any], key_mapping: List[Tuple[str, str, [str|None|List]]], mapped_attrs_dict: Optional[Dict[str, Any]] = None) -> List[Any]:
    """Map biostudies.Submission objects to either semantic_models or bia_data_model equivalent

    """
    sections = find_sections_recursive(submission.section, section_name)

    return_list = []
    for section in sections:
        if mapped_attrs_dict is None:
            attr_dict = attributes_to_dict(section.attributes)
        else:
            attr_dict = mattributes_to_dict(section.attributes, mapped_attrs_dict)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        return_list.append(mapped_object.model_validate(model_dict))
    return return_list

# TODO: Put comments and docstring
def get_generic_section_as_dict(submission: Submission, section_name: List[str], mapped_object: [Any], key_mapping: List[Tuple[str, str, [str|None|List]]]) -> Dict[str,Any]:
    """Map biostudies.Submission objects to dict containing either semantic_models or bia_data_model equivalent

    """
    sections = find_sections_recursive(submission.section, section_name)

    return_dict = {}
    for section in sections:
        attr_dict = attributes_to_dict(section.attributes)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        return_dict[section.accno] = mapped_object.model_validate(model_dict)
    return return_dict

def get_affiliation(submission: Submission) -> Dict[str, semantic_models.Affiliation]:
    """Maps biostudies.Submission.Organisation sections to semantic_models.Affiliations

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
        affiliation_dict[section.accno] = semantic_models.Affiliation.model_validate(model_dict)

    return affiliation_dict


def get_publication(submission: Submission) -> List[semantic_models.Publication]:
    publication_sections = find_sections_recursive(submission.section, ["publication",], [])
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
        publications.append(semantic_models.Publication.model_validate(model_dict))

    return publications

def get_contributor(submission: Submission) -> List[semantic_models.Contributor]:
    """ Map authors in submission to semantic_model.Contributors

    """
    affiliation_dict = get_affiliation(submission) 
    key_mapping = [
        ("display_name", "Name", None),
        ("contact_email", "E-mail", "not@supplied.com"),
        ("role", "Role", None),
        ("orcid", "ORCID", None),
        ("affiliation", "affiliation", []),
    ]
    author_sections = find_sections_recursive(submission.section, ["author",], [])
    contributors = []
    for section in author_sections:
        attr_dict = mattributes_to_dict(section.attributes, affiliation_dict)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        # TODO: Find out if authors can have more than one organisation ->
        #       what are the implications for mattributes_to_dict?
        if model_dict["affiliation"] is None:
            model_dict["affiliation"] = []
        elif type(model_dict["affiliation"]) is not list:
            model_dict["affiliation"] = [model_dict["affiliation"],]
        contributors.append(semantic_models.Contributor.model_validate(model_dict))

    return contributors
    

def find_sections_recursive(
    section: Section, search_types: List[str], results: Optional[List[Section]] = []
) -> List[Section]:
    """Find all sections of search_types within tree, starting at given section

    """

    search_types_lower = [ s.lower() for s in search_types ]
    if section.type.lower() in search_types_lower:
        results.append(section)

    # Each thing in section.subsections is either Section or List[Section]
    # First, let's make sure we ensure they're all lists:
    nested = [
        [item] if not isinstance(item, list) else item for item in section.subsections
    ]
    # Then we can flatten this list of lists:
    flattened = sum(nested, [])

    for section in flattened:
        find_sections_recursive(section, search_types, results)

    return results

# TODO check type of reference_dict. Possibly Dict[str, str], but need to
# verify. This also determines type returned by function
def mattributes_to_dict(attributes: List[Attribute], reference_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Return attributes as dictionary dereferencing attribute references

    Return the list of attributes supplied as a dictionary. Any attributes
    whose values are references are 'dereferenced' using the reference_dict
    """
    def value_or_dereference(attr):
        if attr.reference:
            return reference_dict[attr.value]
        else:
            return attr.value

    return {attr.name: value_or_dereference(attr) for attr in attributes}


# TODO: Need to use a canonical version for this function e.g. from API
def dict_to_uuid(my_dict: Dict[str, Any], attributes_to_consider: List[str]) -> str:
    """Create uuid from specific keys in a dictionary

    """

    seed = "".join([f"{my_dict[attr]}" for attr in attributes_to_consider])
    hexdigest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return str(uuid.UUID(version=4, hex=hexdigest))
