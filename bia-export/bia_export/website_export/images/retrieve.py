from uuid import UUID
from bia_export.website_export.generic_object_retrieval import (
    read_all_json,
    read_file_by_uuid_and_type,
    get_all_api_results,
)
from bia_export.bia_client import api_client
from .models import ImageCLIContext
from bia_integrator_api import models as api_models
from typing import List
import logging

logger = logging.getLogger("__main__." + __name__)


def retrieve_images(
    context: ImageCLIContext,
) -> list[api_models.Image]:
    if context.root_directory:
        api_images: List[api_models.Image] = read_all_json(
            object_type=api_models.Image,
            context=context,
        )

    else:
        dataset_list = get_all_api_results(
            context.study_uuid, api_client.get_dataset_linking_study
        )
        api_images = []
        for dataset in dataset_list:
            api_images += get_all_api_results(
                dataset.uuid,
                api_client.get_image_linking_dataset,
            )

    return api_images


def retrieve_representations(
    image_uuid: UUID, context: ImageCLIContext
) -> List[api_models.ImageRepresentation]:
    if context.root_directory:
        api_img_reps = []
        if image_uuid in context.image_to_rep_uuid_map.keys():
            for img_rep in context.image_to_rep_uuid_map[image_uuid]:
                api_img_reps.append(
                    read_file_by_uuid_and_type(
                        str(img_rep), api_models.ImageRepresentation, context
                    )
                )
    else:
        api_img_reps = get_all_api_results(
            image_uuid, api_client.get_image_representation_linking_image
        )
    return api_img_reps


def get_local_img_rep_map(context: ImageCLIContext) -> dict[UUID, UUID]:
    api_image_represenation: List[api_models.ImageRepresentation] = read_all_json(
        object_type=api_models.ImageRepresentation, context=context
    )
    image_to_rep_map: dict[UUID, List[UUID]] = {}
    for image_rep in api_image_represenation:
        if image_rep.representation_of_uuid not in image_to_rep_map:
            image_to_rep_map[image_rep.representation_of_uuid] = []
        image_to_rep_map[image_rep.representation_of_uuid].append(image_rep.uuid)

    return image_to_rep_map


def retrieve_study(study_uuid: UUID) -> api_models.Study:
    study = api_client.get_study(str(study_uuid), 1)
    return study
