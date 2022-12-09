import logging
from typing import List, Optional

import click
from bia_integrator_core.models import BIAFile, BIAStudy, BIAImage, BIAImageRepresentation, Author, BIAFileRepresentation
from bia_integrator_core.study import persist_study

from bia_integrator_tools.biostudies import (
    File,
    Submission,
    Section,
    attributes_to_dict,
    load_submission,
    file_uri,
    find_files_in_submission
)

logger = logging.getLogger(__file__)


IMAGE_EXTS = ['.png', '.czi', '.tif', '.lsm', '.ims', '.lif', '.tiff', '.nd2', '.ome.tiff', '.dv', '.svs']
ARCHIVE_EXTS = ['.zip']


def is_image(file: File) -> bool:
    return file.path.suffix in IMAGE_EXTS


def author_section_to_author(author_section: Section) -> Author:
    attributes_dict = attributes_to_dict(author_section.attributes)
    
    return Author(name=attributes_dict['Name'])


def find_authors_in_submission(submission: Submission):
    
    authors = []
    for section in submission.section.subsections:
        if section.type == 'author':
            authors.append(author_section_to_author(section))
            
    return authors


def bst_submission_to_bia_study(submission: Submission) -> BIAStudy:
    
    submission_attr_dict = attributes_to_dict(submission.attributes)
    study_section_attr_dict = attributes_to_dict(submission.section.attributes)
    
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
    
    accession_id = submission.accno
    
    all_files = find_files_in_submission(submission)
    image_files = []
    other_files = []
    archive_files = []

    for file in all_files:
        if file.path.suffix in IMAGE_EXTS:
            image_files.append(file)
        elif file.path.suffix in ARCHIVE_EXTS:
            archive_files.append(file)
        else:
            other_files.append(file)

    logger.info(f"Submission has {len(all_files)} files, of which {len(image_files)} are images and {len(archive_files)} are archive files.")

    images = {}
    for n, imfile in enumerate(image_files, start=1):
        image_id = f"IM{n}"
        rep = BIAImageRepresentation(
            accession_id=accession_id,
            image_id=image_id,
            uri=file_uri(accession_id, imfile),
            size=imfile.size,
            type="fire_object",
            dimensions=None,
            attributes = {}
        )
        images[image_id] = BIAImage(
            dimensions=None,
            id=image_id,
            representations=[rep],
            original_relpath=imfile.path,
            attributes=attributes_to_dict(imfile.attributes)
        )   

    study_title = submission_attr_dict.get("Title", None)
    if not study_title:
        study_title = study_section_attr_dict.get("Title", "Unknown")

    bia_study = BIAStudy(
        accession_id=accession_id,
        title=study_title,
        authors=find_authors_in_submission(submission),
        release_date=submission_attr_dict['ReleaseDate'],
        description=study_section_attr_dict['Description'],
        organism=study_section_attr_dict.get('Organism', "Unknown"),
        imaging_type=imaging_method,
        example_image_uri=f"{accession_id}-example.png",
        images=images
    )

    archivefiles = {}
    for n, file in enumerate(archive_files, start=1):
        archive_id = f"Z{n}"
        archivefiles[archive_id] = BIAFile(
            id=archive_id,
            original_relpath=file.path,
            original_size=file.size,
            representations=[
                BIAFileRepresentation(
                    accession_id=accession_id,
                    file_id=archive_id,
                    uri=file_uri(accession_id, file),
                    size=file.size
                )
            ],
            attributes=attributes_to_dict(file.attributes)
        )
    bia_study.archive_files = archivefiles

    # FIXME - horrible variable naming, but it matches the images case above
    otherfiles = {}
    for n, otherfile in enumerate(other_files, start=1):
        other_id = f"O{n}"
        otherfiles[other_id] = BIAFile(
            id=other_id,
            original_relpath=otherfile.path,
            original_size=otherfile.size,
            representations=[
                BIAFileRepresentation(
                    accession_id=accession_id,
                    file_id=other_id,
                    uri=file_uri(accession_id, otherfile),
                    size=otherfile.size
                )
            ],
            attributes=attributes_to_dict(otherfile.attributes)
        )
    bia_study.other_files = otherfiles



    return bia_study


@click.command()
@click.argument("accession_id")
def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    logger.info(f"Fetching {accession_id}")

    bst_submission = load_submission(accession_id)
    bia_study = bst_submission_to_bia_study(bst_submission)
    persist_study(bia_study)


if __name__ == "__main__":
    main()