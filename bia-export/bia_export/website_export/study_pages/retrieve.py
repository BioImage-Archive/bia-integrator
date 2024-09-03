from glob import glob
from uuid import UUID
from bia_export.website_export.utils import read_all_json, read_api_json_file
from pathlib import Path
from bia_export.website_export.website_models import CLIContext
from bia_shared_datamodels import bia_data_model, semantic_models
import json
from typing import List, Type
import logging

logger = logging.getLogger("__main__." + __name__)


def retrieve_study(context: CLIContext) -> bia_data_model.Study:
    if context.root_directory:
        study_path = context.root_directory.joinpath(
            f"studies/{context.accession_id}.json"
        )

        logger.info(f"Loading study from {study_path}")

        api_study = read_api_json_file(study_path, bia_data_model.Study)
    else:
        # TODO: use client and context.study_uuid
        raise NotImplementedError

    return api_study


def retrieve_experimental_imaging_datasets(
    context: CLIContext,
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


def retrieve_aggregation_fields(dataset_uuid: UUID, context: CLIContext):
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


def aggregate_file_list_data(context: CLIContext) -> dict[UUID, dict]:
    dataset_counts_map = {}
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
        if submission_dataset not in dataset_counts_map:
            dataset_counts_map[submission_dataset] = {
                "file_count": 0,
                "image_count": 0,
                "file_type_aggregation": set(),
            }
        dataset_counts_map[submission_dataset]["file_count"] += 1
        dataset_counts_map[submission_dataset]["file_type_aggregation"].add(file_type)
    return dataset_counts_map


def retrieve_dataset_images(
    dataset_uuid: UUID,
    image_type: Type[semantic_models.AbstractImageMixin],
    context: CLIContext,
) -> List[bia_data_model.ExperimentallyCapturedImage]:
    if context.root_directory:

        directory_map = {
            bia_data_model.ExperimentallyCapturedImage: "experimentally_captured_images",
            bia_data_model.DerivedImage: "derived_images",
        }

        image_directory = context.root_directory.joinpath(
            f"{directory_map[image_type]}/{context.accession_id}/*.json"
        )
        all_api_images = read_all_json(image_directory, image_type)
        api_images = [
            image
            for image in all_api_images
            if image.submission_dataset_uuid == dataset_uuid
        ]

    else:
        # TODO: impliment client code
        raise NotImplementedError
    return api_images


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


def retrieve_detail_objects(
    dataset: bia_data_model.ExperimentalImagingDataset,
    detail_map: dict,
    context: CLIContext,
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


def retrieve_image_annotatation_datasets(
    context: CLIContext,
) -> List[bia_data_model.ImageAnnotationDataset]:
    if context.root_directory:
        iad_directory = context.root_directory.joinpath(
            f"image_annotation_datasets/{context.accession_id}/*.json"
        )

        api_aids: List[bia_data_model.ImageAnnotationDataset] = read_all_json(
            iad_directory, bia_data_model.ImageAnnotationDataset
        )
    else:
        # TODO: use client and context.study_uuid
        raise NotImplementedError

    return api_aids


def retrieve_annotion_method(
    api_dataset: bia_data_model.ImageAnnotationDataset, context: CLIContext
):
    if context.root_directory:
        api_methods = []
        methods_directory = context.root_directory.joinpath(
            f"annotation_methods/{context.accession_id}/*.json"
        )
        all_api_methods: List[bia_data_model.AnnotationMethod] = read_all_json(
            methods_directory, bia_data_model.AnnotationMethod
        )
        for api_method in all_api_methods:
            # Note that currentlt the title_ids are the same because the two objects are created from the same user input.
            if api_method.title_id == api_dataset.title_id:
                api_methods.append(api_method)
    else:
        # TODO: use client and context.study_uuid
        raise NotImplementedError
    return api_methods
