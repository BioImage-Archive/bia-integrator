from pathlib import Path
import json
import logging
from .website_models import (
    Study,
    ExperimentalImagingDataset,
    ImageAcquisition,
    BioSample,
    SpecimenGrowthProtocol,
    SpecimenImagingPrepartionProtocol,
)
from glob import glob
from typing import List, Type
from bia_shared_datamodels import bia_data_model
from pydantic import BaseModel

logger = logging.getLogger(__name__)


def read_api_json_file(file_path: Path, object_type: Type[BaseModel]) -> BaseModel:
    """
    Returns model of object from file to be equivalent to using BIA API Client
    """
    with open(file_path, "r") as object_file:
        object_dict = json.load(object_file)

    return object_type(**object_dict)


def read_all_json(
    directory_path: Path, object_type: Type[BaseModel]
) -> List[BaseModel]:
    object_list = []
    file_paths = sorted(glob(str(directory_path)))
    for file_path in file_paths:
        object_list.append(read_api_json_file(file_path, object_type))
    return object_list


def find_associated_objects(
    typed_associations: set,
    directory_path: Path,
    object_type: Type[bia_data_model.UserIdentifiedObject],
) -> List[dict]:
    linked_object = []

    if len(typed_associations) == 0:
        return linked_object

    typed_object_in_study: List[bia_data_model.UserIdentifiedObject] = read_all_json(
        directory_path, object_type
    )
    for object in typed_object_in_study:
        if object.title_id in typed_associations:
            linked_object.append(object.model_dump())
    return linked_object


def create_study(accession_id: str, root_directory: Path) -> Study:

    if root_directory:
        study_path = root_directory.joinpath(f"studies/{accession_id}.json")

        logger.info(f"Loading study from {study_path}")

        api_study = read_api_json_file(study_path, bia_data_model.Study)
    else:
        # TODO: use client
        raise NotImplementedError
    study_dict = api_study.model_dump()
    study_dict["experimental_imaging_component"] = create_experimental_imaging_datasets(
        accession_id, root_directory
    )
    study = Study(**study_dict)

    return study


def create_experimental_imaging_datasets(
    accession_id: str, root_directory: Path = None
) -> List[ExperimentalImagingDataset]:
    eid_list = []
    if root_directory:

        eid_directory = root_directory.joinpath(
            f"experimental_imaging_datasets/{accession_id}/*.json"
        )

        api_eids: List[bia_data_model.ExperimentalImagingDataset] = read_all_json(
            eid_directory, bia_data_model.ExperimentalImagingDataset
        )

        detail_map = {
            ImageAcquisition: {
                "source_directory": "image_acquisitions",
                "association_field": "image_acquisition",
                "bia_type": bia_data_model.ImageAcquisition,
                "previously_displayed": set(),
            },
            BioSample: {
                "source_directory": "biosamples",
                "association_field": "biosample",
                "bia_type": bia_data_model.BioSample,
                "previously_displayed": set(),
            },
            SpecimenImagingPrepartionProtocol: {
                "source_directory": "specimen_imaging_preparation_protocols",
                "association_field": "specimen",
                "bia_type": bia_data_model.SpecimenImagingPrepartionProtocol,
                "previously_displayed": set(),
            },
            SpecimenGrowthProtocol: {
                "source_directory": "specimen_growth_protocols",
                "association_field": "specimen",
                "bia_type": bia_data_model.SpecimenGrowthProtocol,
                "previously_displayed": set(),
            },
        }

        def process_details_section(
            root_directory: Path,
            accession_id: str,
            detail_map_info: dict,
            typed_associations: set,
        ):

            detail_path = root_directory.joinpath(
                f"{detail_map_info['source_directory']}/{accession_id}/*.json"
            )
            detail_linked_to_dataset = find_associated_objects(
                typed_associations,
                detail_path,
                detail_map_info["bia_type"],
            )

            for detail in detail_linked_to_dataset:
                if detail["uuid"] not in detail_map_info["previously_displayed"]:
                    detail["default_open"] = True
                    detail_map_info["previously_displayed"].add(detail["uuid"])
                else:
                    detail["default_open"] = False

            return detail_linked_to_dataset

        for eid in api_eids:
            eid_dict = eid.model_dump()

            associations = eid.attribute["associations"]

            association_by_type = {
                "biosample": set(),
                "image_acquisition": set(),
                "specimen": set(),
            }
            for association in associations:
                for key in association_by_type.keys():
                    association_by_type[key].add(association[key])

            eid_dict["biological_entity"] = process_details_section(
                root_directory,
                accession_id,
                detail_map[BioSample],
                association_by_type["biosample"],
            )
            eid_dict["specimen_imaging_preparation_protocol"] = process_details_section(
                root_directory,
                accession_id,
                detail_map[SpecimenImagingPrepartionProtocol],
                association_by_type["specimen"],
            )
            eid_dict["specimen_growth_protocol"] = process_details_section(
                root_directory,
                accession_id,
                detail_map[BioSample],
                association_by_type["specimen"],
            )
            eid_dict["acquisition_process"] = process_details_section(
                root_directory,
                accession_id,
                detail_map[ImageAcquisition],
                association_by_type["image_acquisition"],
            )

            eid = ExperimentalImagingDataset(**eid_dict)
            eid_list.append(eid)

    return eid_list
