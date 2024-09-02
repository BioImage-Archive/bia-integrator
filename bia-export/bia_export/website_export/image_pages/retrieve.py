from uuid import UUID
from pydantic import BaseModel
from bia_export.website_export.utils import read_all_json, read_api_json_file
from bia_export.website_export.website_models import CLIContext
from bia_shared_datamodels import bia_data_model
from typing import List, Type
import logging

logger = logging.getLogger("__main__." + __name__)


def retrieve_images(
    context: CLIContext,
) -> list[bia_data_model.ImageRepresentation]:

    if context.root_directory:
        image_directory = context.root_directory.joinpath(
            f"experimentally_captured_images/{context.accession_id}/*.json"
        )
        api_ecis: List[bia_data_model.ExperimentallyCapturedImage] = read_all_json(
            image_directory, bia_data_model.ExperimentallyCapturedImage
        )

    else:
        # TODO: implement client
        raise NotImplementedError

    return api_ecis


def retrieve_specimen(
    specimen_uuid: UUID, context: CLIContext
) -> bia_data_model.Specimen:
    if context.root_directory:
        specimen_path = context.root_directory.joinpath(
            f"specimens/{context.accession_id}/{specimen_uuid}.json"
        )
        api_specimen: bia_data_model.Specimen = read_api_json_file(
            specimen_path, bia_data_model.Specimen
        )
    else:
        # TODO: implement API client verison
        raise NotImplementedError
    return api_specimen


def retrieve_object_list(
    uuid_list: list[UUID], api_class: Type[BaseModel], context: CLIContext
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
        # TODO: impliment API client version
        raise NotImplementedError
    return obj_list


def retrieve_canonical_representation(
    image_uuid: UUID, context: CLIContext
) -> bia_data_model.ImageRepresentation:
    if context.root_directory:
        canonical_rep = context.root_directory.joinpath(
            f"image_representations/{context.accession_id}/{str(context.image_to_canonical_rep_uuid_map[image_uuid])}.json"
        )
        canonical_image_represenation: List[bia_data_model.ImageRepresentation] = (
            read_api_json_file(canonical_rep, bia_data_model.ImageRepresentation)
        )
    else:
        # TODO: impliment API client version
        raise NotImplementedError
    return canonical_image_represenation


def is_canonical(image_rep: bia_data_model.ImageRepresentation) -> bool:
    # TODO: create better / more consistent logic to determine the canonical image rep
    # i.e. the one with all the dimension & ome-zarr info we need for the website.
    if image_rep.physical_size_x:
        return True
    else:
        return False


def get_local_img_rep_map(context: CLIContext) -> dict[UUID, UUID]:
    image_rep_path = context.root_directory.joinpath(
        f"image_representations/{context.accession_id}/*.json"
    )
    api_image_represenation: List[bia_data_model.ImageRepresentation] = read_all_json(
        image_rep_path, bia_data_model.ImageRepresentation
    )
    image_to_rep_map = {}
    for image_rep in api_image_represenation:
        if is_canonical(image_rep):
            image_to_rep_map[image_rep.representation_of_uuid] = image_rep.uuid

    return image_to_rep_map
