from typing import List, Dict
import hashlib
import uuid

import rich

from .models import Author, BIAStudy, Affiliation, Publication
from .biostudies import Section, Submission, Attribute, attributes_to_dict

# Import these from API models
from bia_integrator_api.models.biosample import Biosample
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.models.image_acquisition import ImageAcquisition


def find_sections_recursive(section: Section, search_types: List[str], results=[]):
    """Find all sections of the given type within the tree, starting at
    the given section."""

    for search_type in search_types:
        if section.type == search_type:
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


def find_sections_in_submission(submission: Submission, search_types: List[str]):
    """Find all sections within the submission with the given type."""

    return find_sections_recursive(submission.section, search_types, [])


def mattributes_to_dict(attributes: List[Attribute], reference_dict: Dict) -> dict:
    def value_or_dereference(attr):
        if attr.reference:
            return reference_dict[attr.value]
        else:
            return attr.value

    return {attr.name: value_or_dereference(attr) for attr in attributes}


def flatten_mixed_list(iterable):
    # Each thing in section.subsections is either Section or List[Section]
    # First, let's make sure we ensure they're all lists:
    nested = [[item] if not isinstance(item, list) else item for item in iterable]
    # Then we can flatten this list of lists:
    return sum(nested, [])


def find_attribute_values_recursive(section: Section, name: str, results=[]):
    attr_dict = attributes_to_dict(section.attributes)

    if name in attr_dict:
        results.append((section.type, attr_dict[name]))

    to_visit = flatten_mixed_list(section.subsections)

    for section in to_visit:
        find_attribute_values_recursive(section, name, results)

    return results


def recursive_descent(section: Section, depth=0):
    spacing = depth * "  "
    attr_dict = attributes_to_dict(section.attributes)
    print(f"{spacing}{section.type} {','.join(attr_dict.keys())}")

    to_visit = flatten_mixed_list(section.subsections)

    for section in to_visit:
        recursive_descent(section, depth + 1)


def find_attributes_in_submission(submission, name):
    attr_dict = attributes_to_dict(submission.attributes)

    results = []
    if name in attr_dict:
        results.append(("Root", attr_dict[name]))

    return find_attribute_values_recursive(submission.section, name, results)


def find_attributes_by_section_type(submission, key, section_types):
    results = dict(find_attributes_in_submission(submission, key))

    for section_type in section_types:
        if section_type in results:
            return results[section_type]


def extract_model_dict(submission):

    # recursive_descent(submission.section)

    # title = dict(results)["Root"]

    # TODO: Keywords

    description = find_attributes_by_section_type(
        submission, "Description", ["Root", "Study"]
    )
    title = find_attributes_by_section_type(submission, "Title", ["Root", "Study"])
    release_date = find_attributes_by_section_type(
        submission, "ReleaseDate", ["Root", "Study"]
    )

    authors = find_and_convert_authors(submission)

    publications = find_and_convert_publications(submission)

    # bia_study = BIAStudy(
    #         title=title,
    #         description=description,
    #         release_date=release_date,
    #         keywords=[],
    #         authors=authors
    # )

    funding = find_attributes_by_section_type(
        submission, "Funding statement", ["Study"]
    )
    if funding is None:
        funding = ""
    model_dict = {
        "title": title,
        "description": description,
        "release_date": release_date,
        "authors": authors,
        "publications": publications,
        "funding": funding,
    }
    rich.print(model_dict)

    return model_dict

    # rich.print(bia_study)


def find_and_convert_publications(submission):

    sections = find_sections_in_submission(submission, ["Publication"])
    model = Publication
    key_mapping = [
        ("title", "Title", None),
        ("authors", "Authors", None),
        ("doi", "DOI", None),
        ("year", "Year", None),
        ("pubmed_id", "PubMedID", None),
    ]

    publications = []
    for section in sections:
        attr_dict = attributes_to_dict(section.attributes)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        publications.append(model(**model_dict))

    return publications


def find_and_convert_authors(submission):
    organisation_sections = find_sections_in_submission(
        submission, ["organisation", "organization"]
    )

    key_mapping = [("name", "Name", None), ("rorid", "RORID", None)]

    reference_dict = {}
    for section in organisation_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        reference_dict[section.accno] = Affiliation(**model_dict)

    key_mapping = [
        ("name", "Name", None),
        ("email", "E-mail", None),
        ("role", "Role", None),
        ("affiliation", "affiliation", None),
        ("orcid", "ORCID", None),
    ]
    author_sections = find_sections_in_submission(submission, ["author", "Author"])
    authors = []
    for section in author_sections:
        attr_dict = mattributes_to_dict(section.attributes, reference_dict)
        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        authors.append(Author(**model_dict))

    return authors


def dicts_to_api_models(dicts, api_model_class):

    api_models = []
    for model_dict in dicts:
        api_models.append(api_model_class(**model_dict))

    return api_models


def extract_biosample_dicts(submission):
    biosample_sections = find_sections_in_submission(submission, ["Biosample"])

    key_mapping = [
        ("title", "Title", ""),
        ("description", "Description", ""),
        ("biological_entity", "Biological entity", ""),
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
        model_dict["organism_scientific_name"] = organism_scientific_name.strip()
        model_dict["organism_common_name"] = organism_common_name.strip()
        model_dict["organism_ncbi_taxon"] = ""

        # Populate intrinsic and extrinsic variables
        for key in (
            "Intrinsic variable",
            "Extrinsic variable",
            "Experimental variable",
        ):
            model_key = f"{key.lower().replace(' ', '_')}s"
            model_dict[model_key] = []
            if key in attr_dict:
                model_dict[model_key].append(attr_dict[key])

        model_dict["accession_id"] = submission.accno
        model_dict["uuid"] = generate_biosample_uuid(model_dict)
        model_dict["version"] = 0
        model_dicts.append(model_dict)

    return model_dicts


def find_and_convert_biosamples(submission):

    biosample_model_dicts = extract_biosample_dicts(submission)
    biosamples = dicts_to_api_models(biosample_model_dicts, Biosample)
    return biosamples


def extract_specimen_dicts(submission):
    specimen_sections = find_sections_in_submission(submission, ["Specimen"])

    key_mapping = [
        ("title", "Title", ""),
        ("sample_preparation_protocol", "Sample preparation protocol", ""),
        ("growth_protocol", "Growth protocol", ""),
    ]

    model_dicts = []
    for section in specimen_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}
        model_dict["accession_id"] = submission.accno
        model_dict["accno"] = section.__dict__.get("accno", "")
        # Can't compute specimen_uuid without biosample uuid
        # model_dict["uuid"] = dict_to_uuid(model_dict, ["title"])
        model_dict["version"] = 0
        # model_dict["biosample_uuid"] = biosample.uuid
        model_dicts.append(model_dict)

    return model_dicts


def convert_specimen_to_api_model(specimen_dict):

    specimen_dict["uuid"] = generate_specimen_uuid(specimen_dict)
    specimen = dicts_to_api_models([specimen_dict,], Specimen)[0]
    return specimen


def extract_image_acquisition_dicts(submission):
    image_acquisition_sections = find_sections_in_submission(
        submission, ["Image acquisition"]
    )

    key_mapping = [
        ("title", "Title", ""),
        ("imaging_instrument", "Imaging instrument", ""),
        ("image_acquisition_parameters", "Image acquisition parameters", ""),
        ("imaging_method", "Imaging method", ""),
    ]

    model_dicts = []
    for section in image_acquisition_sections:
        attr_dict = attributes_to_dict(section.attributes)

        model_dict = {k: attr_dict.get(v, default) for k, v, default in key_mapping}

        model_dict["accession_id"] = submission.accno
        model_dict["accno"] = section.__dict__.get("accno", "")
        model_dict["version"] = 0
        model_dicts.append(model_dict)

    return model_dicts


def convert_image_acquisition_to_api_model(image_acquisition_dict):

    image_acquisition_dict["uuid"] = generate_image_acquisition_uuid(
        image_acquisition_dict
    )
    image_acquisition = dicts_to_api_models(
        [image_acquisition_dict,], ImageAcquisition
    )[0]
    return image_acquisition


# This function is in bia_integrator_tools.utils !!!
def dict_to_uuid(my_dict: dict, attributes_to_consider: list) -> str:
    """Create uuid from specific keys in a dictionary

    """

    seed = "".join([f"{my_dict[attr]}" for attr in attributes_to_consider])
    hexdigest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return str(uuid.UUID(version=4, hex=hexdigest))


# Generate uuids for specimen, biosample and image_acquisition using
# functions below - these are intended to be called whereever the uuid
# needs to be generated
def generate_biosample_uuid(biosample_dict):
    attributes_to_consider = [
        "accession_id",
        "accno",
        "title",
        "description",
        "biological_entity",
        "organism_scientific_name",
        "organism_common_name",
        "organism_ncbi_taxon",
        "intrinsic_variables",
        "extrinsic_variables",
        "experimental_variables",
    ]
    return dict_to_uuid(biosample_dict, attributes_to_consider)


def generate_specimen_uuid(specimen_dict):
    attributes_to_consider = [
        "accession_id",
        "accno",
        "biosample_uuid",
        "title",
        "sample_preparation_protocol",
        "growth_protocol",
    ]
    return dict_to_uuid(specimen_dict, attributes_to_consider)


def generate_image_acquisition_uuid(image_acquisition):
    attributes_to_consider = [
        "accession_id",
        "accno",
        "specimen_uuid",
        "title",
        "imaging_instrument",
        "image_acquisition_parameters",
        "imaging_method",
    ]
    return dict_to_uuid(image_acquisition, attributes_to_consider)
