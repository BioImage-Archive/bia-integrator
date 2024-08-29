from bia_export.website_export.utils import read_all_json
from bia_export.website_export.website_models import (
    BioSample,
    ImageAcquisition,
    SpecimenGrowthProtocol,
    SpecimenImagingPreparationProtocol,
    StudyCreationContext,
    DetailSection,
)

from bia_shared_datamodels import bia_data_model
from pydantic import BaseModel
from pathlib import Path
from typing import List, Type
import logging

logger = logging.getLogger("__main__." + __name__)


def create_dataset_details(
    dataset: bia_data_model.ExperimentalImagingDataset, context: StudyCreationContext
):

    detail_map = {
        "acquisition_process": {
            "source_directory": "image_acquisitions",
            "association_field": "image_acquisition",
            "bia_type": bia_data_model.ImageAcquisition,
            "website_type": ImageAcquisition,
        },
        "biological_entity": {
            "source_directory": "biosamples",
            "association_field": "biosample",
            "bia_type": bia_data_model.BioSample,
            "website_type": BioSample,
        },
        "specimen_imaging_preparation_protocol": {
            "source_directory": "specimen_imaging_preparation_protocols",
            "association_field": "specimen",
            "bia_type": bia_data_model.SpecimenImagingPreparationProtocol,
            "website_type": SpecimenImagingPreparationProtocol,
        },
        "specimen_growth_protocol": {
            "source_directory": "specimen_growth_protocols",
            "association_field": "specimen",
            "bia_type": bia_data_model.SpecimenGrowthProtocol,
            "website_type": SpecimenGrowthProtocol,
        },
    }

    api_details = retrieve_details(dataset, detail_map, context)

    detail_fields = {}
    for field, object_list in api_details.items():
        detail_fields[field] = []
        for api_object in object_list:
            detail = create_detail(
                api_object,
                detail_map[field]["website_type"],
                context,
            )
            detail_fields[field].append(detail)

    return detail_fields


def retrieve_details(
    dataset: bia_data_model.ExperimentalImagingDataset,
    detail_map: dict,
    context: StudyCreationContext,
) -> dict[str, List]:
    if context.root_directory:
        detail_fields = {}

        association_by_type = {
            "biosample": set(),
            "image_acquisition": set(),
            "specimen": set(),
        }
        for association in dataset.attribute["associations"]:
            for key in association_by_type.keys():
                association_by_type[key].add(association[key])

        for field, source_info in detail_map.items():
            detail_path = context.root_directory.joinpath(
                f"{source_info['source_directory']}/{context.accession_id}/*.json"
            )
            api_objects = find_associated_objects(
                association_by_type[source_info["association_field"]],
                detail_path,
                source_info["bia_type"],
            )
            detail_fields[field] = api_objects

    else:
        # TODO: use client. Either:
        # Dataset -> Images[0] -> specimen -> details (while all images have all the same specimen info)
        # or:
        # Dataset -> details field (when we have multi-hop api endpoints)
        raise NotImplementedError

    return detail_fields


def create_detail(
    detail_object: BaseModel,
    target_type: Type[DetailSection],
    context: StudyCreationContext,
):
    detail_dict = detail_object.model_dump()
    if detail_dict["uuid"] not in context.displayed_dataset_detail[target_type]:
        detail_dict["default_open"] = True
        context.displayed_dataset_detail[target_type].add(detail_dict["uuid"])
    else:
        detail_dict["default_open"] = False
    detail = target_type(**detail_dict)
    return detail


def find_associated_objects(
    typed_associations: set,
    directory_path: Path,
    object_type: Type[bia_data_model.UserIdentifiedObject],
) -> List[bia_data_model.UserIdentifiedObject]:
    linked_object = []

    if len(typed_associations) == 0:
        return linked_object

    # We read all the e.g. Biosamples multiple times per study because there aren't that many and their json is small
    typed_object_in_study: List[bia_data_model.UserIdentifiedObject] = read_all_json(
        directory_path, object_type
    )
    for object in typed_object_in_study:
        if object.title_id in typed_associations:
            linked_object.append(object)
    return linked_object
