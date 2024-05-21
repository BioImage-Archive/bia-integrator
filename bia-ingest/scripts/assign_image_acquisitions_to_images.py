"""Assign Image Acquisitions to Images already in API

"""

import logging


from pathlib import Path

import typer
import os

from bia_ingest.biostudies import (
    load_submission,
    find_file_lists_in_submission,
    flist_from_flist_fname,
)

from bia_integrator_api.exceptions import NotFoundException
from bia_integrator_api.util import simple_client, PrivateApi
from bia_integrator_api.models.biosample import Biosample
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.models.image_acquisition import ImageAcquisition

from bia_ingest.conversion import (
    find_and_convert_biosamples,
    generate_specimen_uuid,
    generate_image_acquisition_uuid,
    extract_biosample_dicts,
    extract_specimen_dicts,
    extract_image_acquisition_dicts,
    dicts_to_api_models,
    dict_to_uuid,
)

logger = logging.getLogger(__file__)

global api_client
api_client = simple_client(
    os.environ.get("BIA_API_BASEPATH", "http://localhost:8080"),
    os.environ.get("BIA_USERNAME", ""),
    os.environ.get("BIA_PASSWORD", ""),
    os.environ.get("BIA_DISABLE_SSL_HOST_CHECK", ""),
)


def image_acquisitions_from_associations(submission, associations):
    """Create/retrieve image acquisition models for specified associations"""

    image_acquisition_dicts = extract_image_acquisition_dicts(submission)
    if len(image_acquisition_dicts) == 0:
        logger.info(f"No image acquisitions for {submission.accno} - exiting")
        return []

    specimen_dicts = extract_specimen_dicts(submission)
    biosample_dicts = extract_biosample_dicts(submission)

    # Retrieve/create API models for image_acquisitions, specimens, biosamples

    # Function to filter appropriate elements from respective dicts
    def _find_element_by_title(title):
        def _inner(item):
            return item.get("title", "") == title

        return _inner

    image_acquisition_uuids = []
    for association in associations:
        # ToDo: Check if there can be > 1 entry with same title? YES!!!
        # ToDo: Refactor code blocks below to iterate using a dict
        image_acquisition_title = association["Image acquisition"]
        image_acquisition = [
            f
            for f in filter(
                _find_element_by_title(image_acquisition_title), image_acquisition_dicts
            )
        ]
        if len(image_acquisition) > 1:
            logger.warning(
                f"Submission has more than one image acquisition with the title {image_acquisition_title}. Using first image acquisition for association {association}"
            )
        image_acquisition = image_acquisition[0]

        specimen_title = association["Specimen"]
        specimen = [
            f for f in filter(_find_element_by_title(specimen_title), specimen_dicts)
        ]
        if len(specimen) > 1:
            logger.warning(
                f"Submission has more than one specimen with the title {specimen_title}. Using first specimen for association {association}"
            )
        specimen = specimen[0]

        biosample_title = association["Biosample"]
        biosample = [
            f for f in filter(_find_element_by_title(biosample_title), biosample_dicts)
        ]
        if len(biosample) > 1:
            logger.warning(
                f"Submission has more than one biosample with the title {biosample_title}. Using first biosample for association {association}"
            )
        biosample = biosample[0]

        # Check if API contains objects with the expected uuids
        try:
            biosample_model = api_client.get_biosample(biosample["uuid"])
            logger.info(
                f"Retrieved biosample with uuid {biosample_model.uuid} using API"
            )
        except NotFoundException:
            biosample_model = dicts_to_api_models([biosample,], Biosample)[0]
            api_client.create_biosample(biosample_model)
            logger.info(f"Created biosample with uuid {biosample_model.uuid}")

        try:
            specimen["biosample_uuid"] = biosample_model.uuid
            specimen["uuid"] = generate_specimen_uuid(specimen)
            specimen_model = api_client.get_specimen(specimen["uuid"])
            logger.info(f"Retrieved specimen with uuid {specimen_model.uuid} using API")
        except NotFoundException:
            specimen_model = dicts_to_api_models([specimen,], Specimen)[0]
            api_client.create_specimen(specimen_model)
            logger.info(f"Created specimen with uuid {specimen_model.uuid}")

        try:
            image_acquisition["specimen_uuid"] = specimen_model.uuid
            image_acquisition["uuid"] = generate_image_acquisition_uuid(
                image_acquisition
            )
            image_acquisition_model = api_client.get_image_acquisition(
                image_acquisition["uuid"]
            )
            logger.info(
                f"Retrieved image_acquisition with uuid {image_acquisition_model.uuid} using API"
            )
        except NotFoundException:
            image_acquisition_model = dicts_to_api_models(
                [image_acquisition,], ImageAcquisition
            )[0]
            api_client.create_image_acquisition(image_acquisition_model)
            logger.info(
                f"Created image_acquisition with uuid {image_acquisition_model.uuid}"
            )
        image_acquisition_uuids.append(image_acquisition_model.uuid)

    return image_acquisition_uuids


def attach_image_acquisitions_to_filerefs(submission):
    """For each file ref return list of image_acquisition uuids"""

    file_list_dicts = find_file_lists_in_submission(submission)
    fileref_to_image_acquisitions = {}
    for file_list_dict in file_list_dicts:
        associations = file_list_dict.get("associations", [])
        n_associations = len(associations)
        if n_associations == 0:
            continue

        image_acquisitions = image_acquisitions_from_associations(
            submission, associations
        )
        if len(image_acquisitions) == 0:
            continue

        # attach image acquisitions to filereferences
        fname = file_list_dict["File List"]
        files_in_fl = flist_from_flist_fname(submission.accno, fname)
        for f in files_in_fl:
            file_dict = {
                "accession_id": submission.accno,
                "path": str(f.path),
                "size": str(f.size),
            }
            fileref_uuid = dict_to_uuid(file_dict, ["accession_id", "path", "size"])
            fileref_to_image_acquisitions[fileref_uuid] = image_acquisitions

    logger.info(
        f"Found {len(fileref_to_image_acquisitions)} fileref to image_acquisition relationships"
    )
    return fileref_to_image_acquisitions


def update_images_with_image_acquisitions(images, fileref_to_image_acquisitions):
    # Types of image representations that represent abstract BIAImage
    bia_image_types = [
        "fire_object",
        "zipped_zarr",
    ]
    for image in images:
        if image.image_acquisitions_uuid is None:
            image.image_acquisitions_uuid = []
        image_acquisitions_uuid = []
        image_reps = [
            i
            for i in filter(
                lambda i: i.type in bia_image_types and "attributes" in i.__dict__,
                image.representations,
            )
        ]
        for image_rep in image_reps:
            for fileref in image_rep.attributes.get("fileref_ids", []):
                image_acquisitions_uuid.extend(
                    fileref_to_image_acquisitions.get(fileref, [])
                )
        if len(image_acquisitions_uuid) > 0:
            image_acquisitions_uuid = list(set(image_acquisitions_uuid))
            image_acquisitions_uuid.sort()
            image.image_acquisitions_uuid.sort()
            if image_acquisitions_uuid != image.image_acquisitions_uuid:
                image.image_acquisitions_uuid = image_acquisitions_uuid
                image.version += 1
                api_client.update_image(image)
                logger.info(
                    f"Setting image {image.uuid} image_acquisitions_uuid to : {image_acquisitions_uuid}"
                )


app = typer.Typer()


@app.command()
def main(accession_id: str):
    logging.basicConfig(level=logging.INFO)

    # If there are no images then nothing to attach image acquisitions to
    study_uuid = api_client.get_object_info_by_accession([accession_id])[0].uuid
    images = api_client.get_study_images(study_uuid)
    if len(images) == 0:
        logger.info(f"No images for {accession_id} - exiting")
        return

    # For each image find file list and attach relevant image acquisition
    bst_submission = load_submission(accession_id)
    fileref_to_image_acquisitions = attach_image_acquisitions_to_filerefs(
        bst_submission
    )
    if len(fileref_to_image_acquisitions) == 0:
        logger.info(f"No image acquisitions for {accession_id} - exiting")
        return

    update_images_with_image_acquisitions(images, fileref_to_image_acquisitions)


if __name__ == "__main__":
    app()
