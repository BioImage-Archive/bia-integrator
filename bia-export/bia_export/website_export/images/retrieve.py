from uuid import UUID
from pydantic import BaseModel
from bia_export.website_export.utils import read_all_json, read_api_json_file
from bia_export.bia_client import api_client
from .models import ImageCLIContext
from bia_shared_datamodels import bia_data_model
from typing import List, Type
import logging

logger = logging.getLogger("__main__." + __name__)


def retrieve_images(
    context: ImageCLIContext,
) -> list[bia_data_model.ExperimentallyCapturedImage]:

    if context.root_directory:
        image_directory = context.root_directory.joinpath(
            f"experimentally_captured_images/{context.accession_id}/*.json"
        )
        api_ecis: List[bia_data_model.ExperimentallyCapturedImage] = read_all_json(
            image_directory, bia_data_model.ExperimentallyCapturedImage
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
) -> bia_data_model.Specimen:
    if context.root_directory:
        specimen_path = context.root_directory.joinpath(
            f"specimens/{context.accession_id}/{specimen_uuid}.json"
        )
        api_specimen: bia_data_model.Specimen = read_api_json_file(
            specimen_path, bia_data_model.Specimen
        )
    else:
        api_specimen = api_client.get_specimen(str(specimen_uuid))
    return api_specimen


def retrieve_object_list(
    uuid_list: list[UUID], api_class: Type[BaseModel], context: ImageCLIContext
) -> List[BaseModel]:
    if context.root_directory:

        # Note could have done this programatically based on class name, but BioSample -> biosamples and not bio_samples.
        # If this changes, recommend using the inflection library
        type_path_map = {
            bia_data_model.BioSample: "biosamples",
            bia_data_model.SpecimenGrowthProtocol: "specimen_growth_protocols",
            bia_data_model.SpecimenImagingPreparationProtocol: "specimen_imaging_preparation_protocols",
            bia_data_model.ImageAcquisition: "image_acquisitions",
        }
        obj_list = []
        for uuid in uuid_list:
            path_name = type_path_map[api_class]
            path = context.root_directory.joinpath(
                f"{path_name}/{context.accession_id}/{uuid}.json"
            )
            obj_list.append(read_api_json_file(path, api_class))
    else:
        obj_list = []
        if api_class == bia_data_model.BioSample:
            for uuid in uuid_list:
                obj_list.append(api_client.get_bio_sample(str(uuid)))
        elif api_class == bia_data_model.SpecimenGrowthProtocol:
            for uuid in uuid_list:
                obj_list.append(api_client.get_specimen_growth_protocol(str(uuid)))
        elif api_class == bia_data_model.SpecimenImagingPreparationProtocol:
            for uuid in uuid_list:
                obj_list.append(
                    api_client.get_specimen_imaging_preparation_protocol(str(uuid))
                )
        elif api_class == bia_data_model.ImageAcquisition:
            for uuid in uuid_list:
                obj_list.append(api_client.get_image_acquisition(str(uuid)))
    return obj_list


def retrieve_representations(
    image_uuid: UUID, context: ImageCLIContext
) -> List[bia_data_model.ImageRepresentation]:
    if context.root_directory:
        api_img_reps = []
        for img_rep in context.image_to_rep_uuid_map[image_uuid]:
            img_rep_path = context.root_directory.joinpath(
                f"image_representations/{context.accession_id}/{str(img_rep)}.json"
            )
            api_img_reps.append(
                read_api_json_file(img_rep_path, bia_data_model.ImageRepresentation)
            )
    else:
        api_img_reps = (
            api_client.get_image_representation_in_experimentally_captured_image(
                str(image_uuid)
            )
        )
    return api_img_reps


def get_local_img_rep_map(context: ImageCLIContext) -> dict[UUID, UUID]:
    image_rep_path = context.root_directory.joinpath(
        f"image_representations/{context.accession_id}/*.json"
    )
    api_image_represenation: List[bia_data_model.ImageRepresentation] = read_all_json(
        image_rep_path, bia_data_model.ImageRepresentation
    )
    image_to_rep_map: dict[UUID, List[UUID]] = {}
    for image_rep in api_image_represenation:
        if image_rep.representation_of_uuid not in image_to_rep_map:
            image_to_rep_map[image_rep.representation_of_uuid] = []
        image_to_rep_map[image_rep.representation_of_uuid].append(image_rep.uuid)

    return image_to_rep_map
