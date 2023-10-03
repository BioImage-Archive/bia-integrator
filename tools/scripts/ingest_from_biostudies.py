import json
import uuid
import logging
import hashlib
import requests
from pathlib import Path
from typing import List 

import click
from bia_integrator_api.models import BIAStudy, FileReference, Author
from bia_integrator_core.interface import persist_study

from bia_integrator_tools.identifiers import file_to_id, dict_to_uuid
from bia_integrator_tools.biostudies import (
    File,
    Submission,
    Section,
    attributes_to_dict,
    load_submission,
    file_uri,
    find_files_in_submission,
    get_file_uri_template_for_accession,
    get_with_case_insensitive_key,
)
from bia_integrator_tools.utils import url_exists


logger = logging.getLogger(__file__)

def bst_file_to_file_reference(accession_id: str, bst_file: File, file_uri_template: str) -> FileReference:

    study_uuid = dict_to_uuid({"accession_id": accession_id,}, attributes_to_consider=["accession_id",])
    fileref_id = file_to_id(accession_id, bst_file)
    fileref_name = str(bst_file.path)
    fileref_attributes = attributes_to_dict(bst_file.attributes)

    fileref = FileReference(
        uuid=fileref_id,
        name=fileref_name,
        uri=file_uri(accession_id, bst_file, file_uri_template=file_uri_template),
        size_in_bytes=bst_file.size,
        attributes=fileref_attributes,
        type=bst_file.type,
        version=0, # For initial creation
        study_uuid=study_uuid
    )

    # If fileref type is directory we may need to append '.zip' to 
    # its uri because FIRE zips directories, but the uri returned by
    # biostudies API as of 02/08/2023 does not include the zip suffix
    if fileref.type == "directory" and not fileref.uri.endswith(".zip"):
        if url_exists(fileref.uri + ".zip"):
            fileref.uri += ".zip"
            logger.info(f"Appended '.zip' to uri of fileref {fileref.id}")
        

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


def get_attr_from_submission(submission: Submission, attr: str) -> str:
    """Search for attr in submission section and if necessary subsections

        Case insensitive search for an attribute in main submission section
        and if not found, search other subsections
    """

    study_components = [
        section
        for section in submission.section.subsections
        if section.type == 'Study Component'
    ]

    if len(study_components):
        for study_component in study_components:
            study_component_attr_dict = attributes_to_dict(study_component.attributes)
            try:
                value = get_with_case_insensitive_key(
                    study_component_attr_dict, attr
                )
                return value
            except KeyError:
                continue
    
    # ToDo: Change search of subsections below to use recursive search
    # similar to bia_integrator_tools.biostudies.find_file_lists_in_section

    # Check other subsections
    other_subsections = [
        section
        for section in submission.section.subsections
        if section.type != 'Study Component'
    ]

    for other_subsection in other_subsections:
        other_subsection_attr_dict = attributes_to_dict(other_subsection.attributes)
        try:
            value = get_with_case_insensitive_key(
                other_subsection_attr_dict, attr
            )
            return value
        except KeyError:
            continue

    return "Unknown"


def bst_submission_to_bia_study(submission: Submission) -> BIAStudy:

    accession_id = submission.accno
    study_uuid = dict_to_uuid({"accession_id": accession_id,}, attributes_to_consider=["accession_id",])
    filerefs_list = filerefs_from_bst_submission(submission)
    filerefs_dict = {fileref.uuid: fileref for fileref in filerefs_list}
    study_title = study_title_from_submission(submission)
    imaging_method = get_attr_from_submission(submission, "Imaging Method")

    study_section_attr_dict = attributes_to_dict(submission.section.attributes)
    submission_attr_dict = attributes_to_dict(submission.attributes)
    try:
        organism = get_with_case_insensitive_key(study_section_attr_dict, "Organism")
    except KeyError:
        organism = get_attr_from_submission(submission, "Organism")

    bia_study = BIAStudy(
        uuid=study_uuid,
        accession_id=accession_id,
        title=study_title,
        authors=find_authors_in_submission(submission),
        release_date=submission_attr_dict['ReleaseDate'],
        description=study_section_attr_dict['Description'],
        organism=organism,
        license=study_section_attr_dict.get('License', "CC0"),
        links=study_links_from_submission(submission),
        imaging_type=imaging_method,
        file_references=filerefs_dict,
        version=0
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
