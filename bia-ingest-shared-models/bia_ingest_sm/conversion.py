from pathlib import Path
import re
import hashlib
import uuid
from typing import List, Any, Dict, Optional, Tuple, Type
from pydantic import BaseModel
from .biostudies import (
    Submission,
    attributes_to_dict,
    Section,
    Attribute,
    find_file_lists_in_submission,
    flist_from_flist_fname,
    file_uri,
)
from . config import settings
from src.bia_models import bia_data_model, semantic_models


def get_file_reference_by_study_component(
        submission: Submission,
        persist_artefacts: bool = False
    ) -> Dict[str, List[bia_data_model.FileReference]]:
    """Return Dict of list of file references in study components.


    """
    file_list_dicts = find_file_lists_in_submission(submission)
    fileref_to_study_components = {}

    if persist_artefacts:
        output_dir = Path(settings.bia_data_dir) / "file_references" / submission.accno
        if not output_dir.is_dir(): output_dir.mkdir(parents=True)

    for file_list_dict in file_list_dicts:
        study_component_name = file_list_dict["Name"]
        if study_component_name not in fileref_to_study_components:
            fileref_to_study_components[study_component_name] = []

        fname = file_list_dict["File List"]
        files_in_fl = flist_from_flist_fname(submission.accno, fname)
        for f in files_in_fl:
            file_dict = {
                "accession_id": submission.accno,
                "file_name": str(f.path),
                "size_in_bytes": str(f.size),
            }
            fileref_uuid = dict_to_uuid(file_dict, ["accession_id", "file_name", "size_in_bytes"])
            fileref_to_study_components[study_component_name].append(fileref_uuid)
            # TODO - Not storing submission_dataset uuid yet!!!
            if persist_artefacts:
                file_dict["uuid"] = fileref_uuid
                file_dict["uri"] = file_uri(submission.accno, f)
                file_dict["submission_dataset"] = fileref_uuid
                file_dict["format"] = f.type
                file_dict["attribute"] = attributes_to_dict(f.attributes)
                file_reference = bia_data_model.FileReference.model_validate(file_dict)
                output_path = output_dir / f"{fileref_uuid}.json"
                output_path.write_text(file_reference.model_dump_json(indent=2))
                

    return fileref_to_study_components


def get_experimental_imaging_dataset(submission: Submission, persist_artefacts=False) -> List[bia_data_model.ExperimentalImagingDataset]:
    """Map biostudies.Submission study components to bia_data_model.ExperimentalImagingDataset

    """
    study_components = find_sections_recursive(submission.section, ["Study Component",], [])
    analysis_method_dict = get_image_analysis_method(submission)

    file_reference_uuids = get_file_reference_by_study_component(submission, persist_artefacts=persist_artefacts)

    # TODO: Need to persist this (API finally, but initially to disk)
    biosamples_in_submission = get_biosample(submission)

    # Index biosamples by title_id. Makes linking with associations more
    # straight forward.
    # Use for loop instead of dict comprehension to allow biosamples with
    # same title to form list
    biosamples_in_submission_uuid = {}
    for biosample in get_biosample(submission, persist_artefacts=persist_artefacts):
        if biosample.title_id in biosamples_in_submission_uuid:
            biosamples_in_submission_uuid[biosample.title_id].append(biosample.uuid)
        else:
            biosamples_in_submission_uuid[biosample.title_id] = [biosample.uuid,]

    experimental_imaging_dataset = []
    for section in study_components:
        attr_dict = attributes_to_dict(section.attributes)
        key_mapping = [
            ("biosample", "Biosample", None,),
            ("specimen", "Specimen", None,),
            ("image_acquisition", "Image acquisition", None,),
            ("image_analysis", "Image analysis", None,),
            ("image_correlation", "Image correlation", None,),
        ]
        associations = get_generic_section_as_list(section, ["Associations",], key_mapping) 

        analysis_method_list = []
        biosample_list = []
        image_acquisition_method_list = []
        correlation_method_list = []
        specimen_preparation_method_list = []

        if len(associations) > 0:
            # Image Analysis Method
            analysis_methods_from_associations = [a.get("image_analysis") for a in associations]
            for analysis_method in analysis_method_dict.values():
                if analysis_method.method_description in analysis_methods_from_associations:
                    analysis_method_list.append(analysis_method)

            # Biosample
            biosamples_from_associations = [a.get("biosample") for a in associations]
            for biosample in biosamples_from_associations:
                if biosample in biosamples_in_submission_uuid:
                    biosample_list.extend(biosamples_in_submission_uuid[biosample])
            
        

        section_name = attr_dict["Name"]
        study_component_file_references =  file_reference_uuids.get(section_name, [])
        model_dict = {
            "title_id": section_name,
            #"description": attr_dict["Description"],
            "submitted_in_study": get_study_uuid(submission),
            "file": study_component_file_references,
            "image": [],
            "specimen_preparation_method": specimen_preparation_method_list,
            "acquisition_method": image_acquisition_method_list,
            "biological_entity": biosample_list,
            "analysis_method": analysis_method_list,
            "correlation_method": correlation_method_list,
            "file_reference_count": len(study_component_file_references),
            "image_count": 0,
            "example_image_uri": [],
        }
        # TODO: Add 'description' to computation of uuid (Maybe accno?)
        model_dict["uuid"] = dict_to_uuid(model_dict, ["title_id", "submitted_in_study", ])
        experimental_imaging_dataset.append(
            bia_data_model.ExperimentalImagingDataset.model_validate(model_dict)
        )
    
    if persist_artefacts and experimental_imaging_dataset:
        output_dir = Path(settings.bia_data_dir) / "experimental_imaging_datasets" / submission.accno
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
        for dataset in experimental_imaging_dataset:
            output_path = output_dir / f"{dataset.uuid}.json"
            output_path.write_text(dataset.model_dump_json(indent=2))

        
    return experimental_imaging_dataset

def get_study(submission: Submission, persist_artefacts: bool = False) -> bia_data_model.Study:
    """Return an API study model populated from the submission

    """

    submission_attributes = attributes_to_dict(submission.attributes)
    contributors = get_contributor(submission)
    grants = get_grant(submission)

    experimental_imaging_datasets = get_experimental_imaging_dataset(submission, persist_artefacts=persist_artefacts)
    experimental_imaging_dataset_uuids = [e.uuid for e in experimental_imaging_datasets]

    study_attributes = attributes_to_dict(submission.section.attributes)

    study_title = study_title_from_submission(submission)
    if "Title" in study_attributes:
        study_attributes.pop("Title")

    licence = get_licence(study_attributes)
    if "License" in study_attributes:
        study_attributes.pop("License")

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
        "keyword": study_attributes.pop("Keywords", []),
        "author": [c.model_dump() for c in contributors],
        "grant": [g.model_dump() for g in grants],
        "attribute": study_attributes,
        "experimental_imaging_component": experimental_imaging_dataset_uuids,
        "annotation_component": [],
    }
    #study_uuid = dict_to_uuid(study_dict, ["accession_id",])
    #study_dict["uuid"] = study_uuid
    study = bia_data_model.Study.model_validate(study_dict)

    if persist_artefacts:
        output_dir = Path(settings.bia_data_dir) / "studies"
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
        output_path = output_dir / f"{study.accession_id}.json"
        output_path.write_text(study.model_dump_json(indent=2))
        # Save ALL file references
        # Save ALL biosamples
        # Save experimental_imaging_datasets
        # Save study
    return study

def get_image_analysis_method(submission: Submission) -> Dict[str, semantic_models.ImageAnalysisMethod]:
    
    key_mapping = [
        ("method_description", "Title", None,),
        ("features_analysed", "Image analysis overview", None,),
    ]
    
    return get_generic_section_as_dict(
        submission, ["Image analysis",], key_mapping, semantic_models.ImageAnalysisMethod
    )

def get_study_uuid(submission: Submission) -> str:
    return dict_to_uuid({"accession_id": submission.accno}, ["accession_id",])

def study_title_from_submission(submission: Submission) -> str:

    submission_attr_dict = attributes_to_dict(submission.attributes)
    study_section_attr_dict = attributes_to_dict(submission.section.attributes)

    study_title = submission_attr_dict.get("Title", None)
    if not study_title:
        study_title = study_section_attr_dict.get("Title", "Unknown")

    return study_title


def get_licence(study_attributes: Dict[str, Any]) -> semantic_models.LicenceType:
    """Return enum version of licence of study

    """
    licence = re.sub(r"\s", "_", study_attributes.get("License", "CC0"))
    return semantic_models.LicenceType(licence)


def get_external_reference(
    submission: Submission,
) -> List[semantic_models.ExternalReference]:
    """Map biostudies.Submission.Link to semantic_models.ExternalReference

    """
    sections = find_sections_recursive(submission.section, ["links",], [])

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
def get_grant(submission: Submission) -> List[semantic_models.Grant]:
    funding_body_dict = get_funding_body(submission)
    key_mapping = [
        ("id", "grant_id", None),
    ]
    grant_dict = get_generic_section_as_dict(
        submission, ["Funding",], key_mapping, semantic_models.Grant )

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
    funding_body = get_generic_section_as_dict(
        submission, ["Funding",], key_mapping, semantic_models.FundingBody
    )
    return funding_body


# TODO: Put comments and docstring
def get_generic_section_as_list(
    root: [Submission|Section],
    section_name: List[str],
    key_mapping: List[Tuple[str, str, [str | None | List]]],
    mapped_object: Optional[Any] = None,
    mapped_attrs_dict: Optional[Dict[str, Any]] = None,
) -> List[Any|Dict[str,str|List[str]]]:
    """Map biostudies.Submission objects to either semantic_models or bia_data_model equivalent

    """
    if type(root) is Submission:
        sections = find_sections_recursive(root.section, section_name, [])
    else:
        sections = find_sections_recursive(root, section_name, [])

    return_list = []
    for section in sections:
        if mapped_attrs_dict is None:
            attr_dict = attributes_to_dict(section.attributes)
        else:
            attr_dict = mattributes_to_dict(section.attributes, mapped_attrs_dict)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        if mapped_object is None:
            return_list.append(model_dict)
        else:
            return_list.append(mapped_object.model_validate(model_dict))
    return return_list


# TODO: Put comments and docstring
def get_generic_section_as_dict(
    root: [Submission|Section],
    section_name: List[str],
    key_mapping: List[Tuple[str, str, [str | None | List]]],
    mapped_object: Optional[Any]=None,
) -> Dict[str, Any|Dict[str, Dict[str,str|List[str]]]]:
    """Map biostudies.Submission objects to dict containing either semantic_models or bia_data_model equivalent

    """
    if type(root) is Submission:
        sections = find_sections_recursive(root.section, section_name, [])
    else:
        sections = find_sections_recursive(root, section_name, [])

    return_dict = {}
    for section in sections:
        attr_dict = attributes_to_dict(section.attributes)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        if mapped_object is None:
            return_dict[section.accno] = model_dict
        else:
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
        affiliation_dict[section.accno] = semantic_models.Affiliation.model_validate(
            model_dict
        )

    return affiliation_dict


def get_publication(submission: Submission) -> List[semantic_models.Publication]:
    publication_sections = find_sections_recursive(
        submission.section, ["publication",], []
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
            model_dict["affiliation"] = [
                model_dict["affiliation"],
            ]
        contributors.append(semantic_models.Contributor.model_validate(model_dict))

    return contributors

# This function instantiates any API model given a dict of its attributes
# Hence the use of the pydantic BaseModel which all API models
# are derived from in the type hinting
def dicts_to_api_models(
    dicts: List[Dict[str, Any]], api_model_class: Type[BaseModel]
) -> BaseModel:

    api_models = []
    for model_dict in dicts:
        api_models.append(api_model_class.model_validate(model_dict))

    return api_models

def get_biosample(submission: Submission, persist_artefacts=False) -> List[bia_data_model.BioSample]:

    biosample_model_dicts = extract_biosample_dicts(submission)
    biosamples = dicts_to_api_models(biosample_model_dicts, bia_data_model.BioSample)

    if persist_artefacts and biosamples:
        output_dir = Path(settings.bia_data_dir) / "biosamples" / submission.accno
        if not output_dir.is_dir():
            output_dir.mkdir(parents=True)
        for biosample in biosamples:
            output_path = output_dir / f"{biosample.uuid}.json"
            output_path.write_text(biosample.model_dump_json(indent=2))
    return biosamples

def extract_biosample_dicts(submission: Submission) -> List[Dict[str, Any]]:
    biosample_sections = find_sections_recursive(submission.section, ["Biosample"], [])

    key_mapping = [
        ("title_id", "Title", ""),
        ("description", "Description", ""),
        # TODO: discuss adding this to semantic model with FS
        #("biological_entity", "Biological entity", ""),
        ("organism", "Organism", ""),
    ]

    model_dicts = []
    for section in biosample_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}

        model_dict["accno"] = section.__dict__.get("accno", "")

        # Obtain scientic and common names from organism
        organism = model_dict.pop("organism", "")
        try:
            organism_scientific_name, organism_common_name = organism.split("(")
            organism_common_name = organism_common_name.rstrip(")")
        except ValueError:
            organism_scientific_name = organism
            organism_common_name = ""
        taxon = semantic_models.Taxon.model_validate({
            "common_name": organism_common_name.strip(),
            "scientific_name": organism_scientific_name.strip(),
            "ncbi_id": None,
        })
        model_dict["organism_classification"] = [ taxon.model_dump() ]

        # Populate intrinsic and extrinsic variables
        for api_key, biostudies_key in (
            ("intrinsic_variable_description", "Intrinsic variable"),
            ("extrinsic_variable_description", "Extrinsic variable",),
            ("experimental_variable_description", "Experimental variable",),
        ):
            model_dict[api_key] = []
            if biostudies_key in attr_dict:
                model_dict[api_key].append(attr_dict[biostudies_key])

        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_biosample_uuid(model_dict)
        model_dicts.append(model_dict)

    return model_dicts


def generate_biosample_uuid(biosample_dict: Dict[str, Any]) -> str:
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title_id",
        "organism_classification",
        "description",
        # TODO: Discuss including below in semantic_models.BioSample
        #"biological_entity",
        "intrinsic_variable_description",
        "extrinsic_variable_description",
        "experimental_variable_description",
    ]
    return dict_to_uuid(biosample_dict, attributes_to_consider)

def find_sections_recursive(
    section: Section, search_types: List[str], results: Optional[List[Section]] = []
) -> List[Section]:
    """Find all sections of search_types within tree, starting at given section

    """

    search_types_lower = [s.lower() for s in search_types]
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
def mattributes_to_dict(
    attributes: List[Attribute], reference_dict: Dict[str, Any]
) -> Dict[str, Any]:
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
