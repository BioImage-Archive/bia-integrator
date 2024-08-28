from bia_export.website_export.dataset_details import create_dataset_details
from bia_export.website_export.utils import read_all_json
from bia_export.website_export.website_models import (
    ExperimentalImagingDataset,
    StudyCreationContext,
)
from uuid import UUID


from bia_shared_datamodels import bia_data_model

import json
from glob import glob
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger("__main__." + __name__)


def create_experimental_imaging_datasets(
    context: StudyCreationContext,
) -> List[ExperimentalImagingDataset]:
    api_datasets = retrieve_experimental_imaging_datasets(context)

    # Collect file list information prior to creating eid if reading locally to avoid reading them multiple times.
    if context.root_directory:
        context.dataset_file_aggregate_data = aggregate_file_list_data(context)

    dataset_list = []
    for api_dataset in api_datasets:
        dataset_list.append(create_experimental_imaging_dataset(api_dataset, context))

    return dataset_list


def retrieve_experimental_imaging_datasets(
    context: StudyCreationContext,
) -> bia_data_model.ExperimentalImagingDataset:
    if context.root_directory:
        eid_directory = context.root_directory.joinpath(
            f"experimental_imaging_datasets/{context.accession_id}/*.json"
        )

        api_eids: List[bia_data_model.ExperimentalImagingDataset] = read_all_json(
            eid_directory, bia_data_model.ExperimentalImagingDataset
        )
    else:
        # TODO: use client and context.study_uuid
        raise NotImplementedError

    return api_eids


def create_experimental_imaging_dataset(
    api_dataset: bia_data_model.ExperimentalImagingDataset,
    context: StudyCreationContext,
) -> ExperimentalImagingDataset:

    dataset_dict = api_dataset.model_dump()

    # Details include Biosample, and various Protocols
    dataset_dict = dataset_dict | create_dataset_details(api_dataset, context)

    dataset_dict = dataset_dict | retrieve_aggregation_fields(api_dataset.uuid, context)

    dataset = ExperimentalImagingDataset(**dataset_dict)
    return dataset


def retrieve_aggregation_fields(dataset_uuid: UUID, context: StudyCreationContext):
    if context.root_directory:
        try:
            dataset_aggregation_fields = context.dataset_file_aggregate_data[
                dataset_uuid
            ]
            dataset_aggregation_fields["file_type_aggregation"] = sorted(
                list(dataset_aggregation_fields["file_type_aggregation"])
            )
        except KeyError:
            dataset_aggregation_fields = {
                "file_count": 0,
                "image_count": 0,
                "file_type_aggregation": [],
            }
    else:
        # TODO: use client and count fields
        raise NotImplementedError
    return dataset_aggregation_fields


def aggregate_file_list_data(context: StudyCreationContext) -> dict[UUID, dict]:
    eid_counts_map = {}
    file_reference_directory = context.root_directory.joinpath(
        f"file_references/{context.accession_id}/*.json"
    )
    file_reference_paths = glob(str(file_reference_directory))
    for file_path in file_reference_paths:
        with open(file_path, "r") as object_file:
            object_dict = json.load(object_file)
            file_reference = bia_data_model.FileReference(**object_dict)
        submission_dataset = file_reference.submission_dataset_uuid
        file_type = Path(file_reference.file_path).suffix
        if submission_dataset not in eid_counts_map:
            eid_counts_map[submission_dataset] = {
                "file_count": 0,
                "image_count": 0,
                "file_type_aggregation": set(),
            }
        eid_counts_map[submission_dataset]["file_count"] += 1
        eid_counts_map[submission_dataset]["file_type_aggregation"].add(file_type)
    return eid_counts_map
