from uuid import UUID
from bia_export.website_export.generic_object_retrieval import (
    get_all_api_results,
)
from bia_export.bia_client import api_client
from bia_integrator_api import models as api_models
import logging

logger = logging.getLogger("__main__." + __name__)


def retrieve_images(
    study_uuid: UUID,
) -> list[api_models.Image]:

    dataset_list = get_all_api_results(study_uuid, api_client.get_dataset_linking_study)
    api_images = []
    for dataset in dataset_list:
        api_images += get_all_api_results(
            dataset.uuid,
            api_client.get_image_linking_dataset,
        )

    return api_images


def retrieve_file_references(
    api_image: api_models.Image,
) -> list[api_models.FileReference]:
    file_references = []

    for uuid in api_image.original_file_reference_uuid:
        file_references.append(api_client.get_file_reference(uuid))

    return file_references


def retrieve_image_representations(image_uuid):
    api_img_reps = get_all_api_results(
        image_uuid, api_client.get_image_representation_linking_image
    )
    return api_img_reps
