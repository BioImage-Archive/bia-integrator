from uuid import UUID
from pydantic import BaseModel
from pydantic.alias_generators import to_snake
from bia_export.website_export.utils import (
    read_all_json,
    read_api_json_file,
    read_file_by_uuid_and_type,
)
from bia_export.bia_client import api_client
from .models import ImageCLIContext
from bia_integrator_api import models as api_models
from typing import List, Type
import logging

logger = logging.getLogger("__main__." + __name__)


def retrieve_images(
    context: ImageCLIContext,
) -> list[api_models.ExperimentallyCapturedImage]:

    if context.root_directory:
        api_ecis: List[api_models.ExperimentallyCapturedImage] = read_all_json(
            object_type=api_models.ExperimentallyCapturedImage,
            context=context,
        )

    else:
        eid_list = api_client.get_experimental_imaging_dataset_in_study(
            str(context.study_uuid)
        )
        api_ecis = []
        for eid in eid_list:
            images = api_client.get_experimentally_captured_image_in_experimental_imaging_dataset(
                str(eid.uuid)
            )
            api_ecis += images

    return api_ecis


def retrieve_specimen(
    specimen_uuid: UUID, context: ImageCLIContext
) -> api_models.Specimen:
    if context.root_directory:

        api_specimen: api_models.Specimen = read_file_by_uuid_and_type(
            specimen_uuid, api_models.Specimen, context
        )

    else:
        api_specimen = api_client.get_specimen(str(specimen_uuid))
    return api_specimen


def retrieve_object_list(
    uuid_list: list[UUID], api_class: Type[BaseModel], context: ImageCLIContext
) -> List[BaseModel]:
    if context.root_directory:
        obj_list = []
        for uuid in uuid_list:
            obj_list.append(read_file_by_uuid_and_type(uuid, api_class, context))
    else:
        obj_list = []
        if api_class == api_models.BioSample:
            for uuid in uuid_list:
                obj_list.append(api_client.get_bio_sample(str(uuid)))

        elif api_class == api_models.SpecimenGrowthProtocol:
            for uuid in uuid_list:
                obj_list.append(api_client.get_specimen_growth_protocol(str(uuid)))

        elif api_class == api_models.SpecimenImagingPreparationProtocol:
            for uuid in uuid_list:
                obj_list.append(
                    api_client.get_specimen_imaging_preparation_protocol(str(uuid))
                )

        elif api_class == api_models.ImageAcquisition:
            for uuid in uuid_list:
                obj_list.append(api_client.get_image_acquisition(str(uuid)))

    return obj_list


def retrieve_representations(
    image_uuid: UUID, context: ImageCLIContext
) -> List[api_models.ImageRepresentation]:
    if context.root_directory:
        api_img_reps = []
        for img_rep in context.image_to_rep_uuid_map[image_uuid]:
            api_img_reps.append(
                read_file_by_uuid_and_type(
                    str(img_rep), api_models.ImageRepresentation, context
                )
            )
    else:
        api_img_reps = (
            api_client.get_image_representation_in_experimentally_captured_image(
                str(image_uuid)
            )
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
