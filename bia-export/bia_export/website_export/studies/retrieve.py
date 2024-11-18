from glob import glob
from uuid import UUID
from bia_export.website_export.generic_object_retrieval import (
    read_all_json,
    read_api_json_file,
    get_source_directory,
    get_all_api_results,
)
from pathlib import Path
from .models import StudyCLIContext
from bia_shared_datamodels import semantic_models, bia_data_model
from bia_integrator_api import models as api_models
import json
from typing import List, Type
import logging
from bia_export.bia_client import api_client

logger = logging.getLogger("__main__." + __name__)


def retrieve_study(context: StudyCLIContext) -> api_models.Study:
    if context.root_directory:
        study_directory = get_source_directory(api_models.Study, context)
        study_paths = glob(str(study_directory))

        if len(study_paths) != 1:
            raise Exception("Unexpected number of study objects")

        study_path = study_paths[0]
        logger.info(f"Loading study from {study_path}")

        api_study = read_api_json_file(study_path, api_models.Study)
    else:
        api_study = api_client.get_study(str(context.study_uuid))

    return api_study


def retrieve_datasets(
    context: StudyCLIContext,
) -> api_models.Dataset:
    if context.root_directory:
        api_datasets: List[api_models.Dataset] = read_all_json(
            object_type=api_models.Dataset, context=context
        )
    else:
        api_datasets = get_all_api_results(
            context.study_uuid, api_client.get_dataset_linking_study
        )

    return api_datasets


def retrieve_aggregation_fields(
    dataset: bia_data_model.DocumentMixin, context: StudyCLIContext
):
    if context.root_directory:
        try:
            dataset_aggregation_fields = context.dataset_file_aggregate_data[
                dataset.uuid
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
        images: List[bia_data_model.Image] = get_all_api_results(
            dataset.uuid, api_client.get_image_linking_dataset
        )
        files: List[bia_data_model.FileReference] = get_all_api_results(
            dataset.uuid, api_client.get_file_reference_linking_dataset
        )

        file_type_aggregation = set()
        for file_reference in files:
            file_type = Path(file_reference.file_path).suffix
            file_type_aggregation.add(file_type)

        dataset_aggregation_fields = {
            "file_count": len(files),
            "image_count": len(images),
            "file_type_aggregation": sorted(list(file_type_aggregation)),
        }

    return dataset_aggregation_fields


def aggregate_file_list_data(context: StudyCLIContext) -> dict[UUID, dict]:
    dataset_counts_map = {}

    file_reference_directory = get_source_directory(api_models.FileReference, context)
    file_reference_paths = glob(str(file_reference_directory))
    for file_path in file_reference_paths:
        with open(file_path, "r") as object_file:
            object_dict = json.load(object_file)
            file_reference = api_models.FileReference(**object_dict)
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

    images_directory = get_source_directory(api_models.Image, context)
    image_paths = glob(str(images_directory))

    for image_path in image_paths:
        with open(image_path, "r") as object_file:
            object_dict = json.load(object_file)
        submission_dataset = object_dict["submission_dataset_uuid"]
        file_type = Path(file_reference.file_path).suffix
        if submission_dataset not in dataset_counts_map:
            dataset_counts_map[submission_dataset] = {
                "file_count": 0,
                "image_count": 0,
                "file_type_aggregation": set(),
            }
        dataset_counts_map[submission_dataset]["image_count"] += 1

    return dataset_counts_map


def retrieve_dataset_images(
    dataset_uuid: UUID,
    image_type: Type[bia_data_model.Image],
    context: StudyCLIContext,
) -> List[api_models.Image]:
    if context.root_directory:

        all_api_images: List[bia_data_model.Image] = read_all_json(
            object_type=image_type, context=context
        )
        api_images = [
            image
            for image in all_api_images
            if image.submission_dataset_uuid == dataset_uuid
        ]

    else:
        api_images = get_all_api_results(
            dataset_uuid, api_client.get_image_linking_dataset
        )

    return api_images


def find_associated_objects(
    typed_associations: set,
    object_type: Type[bia_data_model.UserIdentifiedObject],
    context: StudyCLIContext,
) -> List[bia_data_model.UserIdentifiedObject]:
    linked_object = []

    if len(typed_associations) == 0:
        return linked_object

    # We read all the e.g. Biosamples multiple times per study because there aren't that many and their json is small
    typed_object_in_study: List[bia_data_model.UserIdentifiedObject] = read_all_json(
        object_type=object_type, context=context
    )
    for object in typed_object_in_study:
        if object.title_id in typed_associations:
            linked_object.append(object)
    return linked_object


def retrieve_detail_objects(
    dataset: api_models.Dataset,
    detail_map: dict,
    context: StudyCLIContext,
) -> dict[str, List]:
    if context.root_directory:
        detail_fields = {}

        association_by_type = {
            "biosample": set(),
            "image_acquisition": set(),
            "specimen": set(),
        }
        for attribute in dataset.attribute:
            if attribute.name == "associations":
                for key in association_by_type.keys():
                    association_by_type[key].add(attribute.value[key])

        for field, source_info in detail_map.items():

            api_objects = find_associated_objects(
                association_by_type[source_info["association_field"]],
                source_info["bia_type"],
                context,
            )
            detail_fields[field] = api_objects

    else:
        # Currently performing graph traversal of:
        # Dataset -> Images[0] -> Creation Process-> specimen -> details (while all images have all the same specimen info)
        # but could alternatively switch to the much simpler (for the exporter!):
        # Dataset -> details field (when we have multi-hop api endpoints)
        dataset_images = api_client.get_image_linking_dataset(str(dataset.uuid), 1)

        acquisition_process = []
        biological_entity = []
        specimen_imaging_preparation_protocol = []

        if len(dataset_images) != 0:
            single_dataset_image: bia_data_model.Image = dataset_images[0]
            creation_process = api_client.get_creation_process(
                single_dataset_image.creation_process_uuid
            )

            if creation_process.subject_specimen_uuid:
                specimen = api_client.get_specimen(
                    creation_process.subject_specimen_uuid
                )
                for biosample_uuid in specimen.sample_of_uuid:
                    biological_entity.append(
                        api_client.get_bio_sample(str(biosample_uuid))
                    )
                for sipp_uuid in specimen.imaging_preparation_protocol_uuid:
                    specimen_imaging_preparation_protocol.append(
                        api_client.get_specimen_imaging_preparation_protocol(
                            str(sipp_uuid)
                        )
                    )

            for ia_uuid in creation_process.image_acquisition_protocol_uuid:
                acquisition_process.append(
                    api_client.get_image_acquisition_protocol(str(ia_uuid))
                )

        # TODO: Use detail map to namage field names in a single place
        detail_fields = {
            "acquisition_process": acquisition_process,
            "biological_entity": biological_entity,
            "specimen_imaging_preparation_protocol": specimen_imaging_preparation_protocol,
        }

    return detail_fields
