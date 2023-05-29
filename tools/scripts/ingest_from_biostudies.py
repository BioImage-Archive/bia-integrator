import json
import uuid
import logging
import hashlib
import requests
from pathlib import Path
from typing import List 

import click
from bia_integrator_core.models import BIAStudy, FileReference, Author
from bia_integrator_core.interface import persist_study

from bia_integrator_tools.identifiers import file_to_id
from bia_integrator_tools.biostudies import (
    File,
    Submission,
    Section,
    attributes_to_dict,
    load_submission,
    file_uri,
    find_files_in_submission,
    get_file_uri_template_for_accession
)


logger = logging.getLogger(__file__)

# Get known image extensions
known_image_extensions = []
resource_names = [
    "bioformats_curated_other_file_formats.txt",
    "bioformats_curated_single_file_formats.txt",
]
for resource_name in resource_names:
    resource_path = Path(__file__).parent.parent / "resources" / resource_name
    known_image_extensions.extend([r for r in resource_path.read_text().split("\n") if len(r) > 0])

def bst_file_to_file_reference(accession_id: str, bst_file: File, file_uri_template: str) -> FileReference:

    fileref_id = file_to_id(accession_id, bst_file)
    fileref_name = str(bst_file.path)
    fileref_attributes = attributes_to_dict(bst_file.attributes)

    # To deal with inconsistent URIs associated with directories,
    # If a URI does not end with an extension of a known file format
    # Check that the URI exists. If it does not exist try appending '.zip'
    
    # TODO: Check with MH if changing name/uri breaks anything downstream
    # as uuid computation includes names/uris
    fileref_uri = file_uri(accession_id, bst_file, file_uri_template=file_uri_template)
    suffix = Path(fileref_uri).suffix
    if suffix not in known_image_extensions:
        zip_uri = fileref_uri + ".zip"
        response = requests.head(zip_uri)
        if response.status_code == 200:
            fileref_uri = zip_uri
            fileref_name += ".zip"

    fileref = FileReference(
        id=fileref_id,
        name=fileref_name,
        uri=fileref_uri,
        size_in_bytes=bst_file.size,
        attributes=fileref_attributes
    )

    return fileref


def filerefs_from_bst_submission(submission: Submission) -> List[FileReference]:

    all_files = find_files_in_submission(submission)

    logger.info(f"Creating references for {len(all_files)} files")
    accession_id = submission.accno
    file_uri_template = get_file_uri_template_for_accession(accession_id)

    filerefs = [
        bst_file_to_file_reference(accession_id, bst_file, file_uri_template) for bst_file in all_files
    ]

    return filerefs


def author_section_to_author(author_section: Section) -> Author:

    attributes_dict = attributes_to_dict(author_section.attributes)
    
    return Author(name=attributes_dict['Name'])


def find_authors_in_submission(submission: Submission):
    
    authors = []
    for section in submission.section.subsections:
        if section.type == 'Author' or section.type == 'author':
            authors.append(author_section_to_author(section))
            
    return authors    


def study_title_from_submission(submission: Submission) -> str:

    submission_attr_dict = attributes_to_dict(submission.attributes)
    study_section_attr_dict = attributes_to_dict(submission.section.attributes)

    study_title = submission_attr_dict.get("Title", None)
    if not study_title:
        study_title = study_section_attr_dict.get("Title", "Unknown")

    return study_title

def study_links_from_submission(submission: Submission) -> dict:



    links = {}
    for l in submission.section.links:
        study_link = l.url
        study_link_attr = attributes_to_dict(l.attributes)
        study_link_desc=study_link_attr.get('Description',"Unknown")

        links[study_link_desc] = study_link

    return links


def imaging_method_from_submission(submission: Submission) -> str:

    study_components = [
        section
        for section in submission.section.subsections
        if section.type == 'Study Component'
    ]

    if len(study_components):
        study_component_attr_dict = attributes_to_dict(study_components[0].attributes)
        imaging_method = study_component_attr_dict.get('Imaging Method', "Unknown")
    else:
        imaging_method = "Unknown"

    return imaging_method


def bst_submission_to_bia_study(submission: Submission) -> BIAStudy:

    accession_id = submission.accno
    filerefs_list = filerefs_from_bst_submission(submission)
    filerefs_dict = {fileref.id: fileref for fileref in filerefs_list}
    study_title = study_title_from_submission(submission)
    imaging_method = imaging_method_from_submission(submission)

    study_section_attr_dict = attributes_to_dict(submission.section.attributes)
    submission_attr_dict = attributes_to_dict(submission.attributes)
    bia_study = BIAStudy(
        accession_id=accession_id,
        title=study_title,
        authors=find_authors_in_submission(submission),
        release_date=submission_attr_dict['ReleaseDate'],
        description=study_section_attr_dict['Description'],
        organism=study_section_attr_dict.get('Organism', "Unknown"),
        license=study_section_attr_dict.get('License', "CC0"),
        links=study_links_from_submission(submission),
        imaging_type=imaging_method,
        file_references=filerefs_dict
    )

    return bia_study


@click.command()
@click.argument("accession_id")
def main(accession_id):
    
    logging.basicConfig(level=logging.INFO)

    bst_submission = load_submission(accession_id)
    bia_study = bst_submission_to_bia_study(bst_submission)

    persist_study(bia_study)


if __name__ == "__main__":
    main()
