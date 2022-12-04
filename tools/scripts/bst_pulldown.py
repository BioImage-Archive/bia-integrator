import logging
from typing import List, Optional

import click
from bia_integrator_core.models import BIAStudy, BIAImage, BIAImageRepresentation
from bia_integrator_core.study import persist_study

from bia_integrator_tools.biostudies import (
    Submission,
    attributes_to_dict,
    load_submission,
    file_uri,
    find_files_in_submission
)

logger = logging.getLogger(__file__)


IMAGE_EXTS = ['.png', '.czi', '.tif', '.lsm', '.ims', '.lif', '.tiff', '.nd2', '.ome.tiff']


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
    image_files = [
        file
        for file in all_files
        if is_image(file)
    ]

    logger.info(f"Submission has {len(all_files)} files, of which {len(image_files)} are images.")

    images = {}
    for n, imfile in enumerate(image_files, start=1):
        image_id = f"IM{n}"
        rep = BIAImageRepresentation(
            accession_id=accession_id,
            image_id=image_id,
            uri=file_uri(accession_id, imfile),
            size=imfile.size,
            type="fire_object",
            dimensions=None
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
        release_date=submission_attr_dict['ReleaseDate'],
        description=study_section_attr_dict['Description'],
        organism=study_section_attr_dict.get('Organism', "Unknown"),
        imaging_type=imaging_method,
        example_image_uri=f"{accession_id}-example.png",
        images=images
    )

    return bia_study


def is_image(file):
    return file.path.suffix in IMAGE_EXTS


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