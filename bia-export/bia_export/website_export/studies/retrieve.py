from glob import glob
from uuid import UUID
from bia_export.website_export.generic_object_retrieval import (
    read_all_json,
    read_api_json_file,
    get_source_directory,
    get_all_api_results,
    retrieve_object,
)
from pathlib import Path
from pydantic import ValidationError
from pydantic.alias_generators import to_snake
from .models import StudyCLIContext, CacheUse
from bia_shared_datamodels import bia_data_model, attribute_models
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

    # The cache and the export from local files both store information in context.dataset_file_aggregate_data
    if context.root_directory or (
        context.cache_use == CacheUse.READ_CACHE
        and context.dataset_file_aggregate_data
        and str(dataset.uuid) in context.dataset_file_aggregate_data
    ):
        try:
            dataset_aggregation_fields = context.dataset_file_aggregate_data[
                str(dataset.uuid)
            ]
            if context.cache_use == CacheUse.WRITE_CACHE:
                write_to_cache(dataset.uuid, dataset_aggregation_fields)

        except KeyError:
            logger.warning(f"Could not find aggregate data for dataset: {dataset.uuid}")
            dataset_aggregation_fields = {
                "file_reference_count": 0,
                "image_count": 0,
                "file_reference_size_bytes": 0,
                "file_type_counts": {},
            }
    else:
        retry_count = 0
        max_retry_count = 5
        dataset_stats = None
        while not dataset_stats and retry_count < max_retry_count:
            try:
                dataset_stats = api_client.get_dataset_stats(dataset.uuid)
            except:
                retry_count += 1
                if retry_count == max_retry_count:
                    logger.warning(
                        f"Failed to fetch dataset stats for {dataset.uuid} after {max_retry_count} attemps"
                    )

        if dataset_stats:
            dataset_aggregation_fields = dataset_stats.model_dump()
        else:
            dataset_aggregation_fields = {
                "file_reference_count": 0,
                "image_count": 0,
                "file_reference_size_bytes": 0,
                "file_type_counts": {},
            }
        if context.cache_use == CacheUse.WRITE_CACHE:
            write_to_cache(dataset.uuid, dataset_aggregation_fields)

    return dataset_aggregation_fields


def write_to_cache(dataset_uuid, aggregation_fields):
    logging.info(f"writing to dataset aggregation cache for dataset: {dataset_uuid}")

    cache_file = (
        Path(__file__).parents[3].absolute()
        / "cached_computed_data"
        / "dataset_aggregate_fields.json"
    )
    with open(cache_file, "r") as object_file:
        try:
            object_dict = json.load(object_file)
        except:
            object_dict = {}

    object_dict[str(dataset_uuid)] = aggregation_fields

    with open(cache_file, "w") as object_file:
        object_file.write(json.dumps(object_dict, indent=4))


def aggregate_file_list_data(context: StudyCLIContext) -> None:
    if context.cache_use == CacheUse.READ_CACHE:
        cache_file = (
            Path(__file__).parents[3].absolute()
            / "cached_computed_data"
            / "dataset_aggregate_fields.json"
        )

        with open(cache_file, "r") as object_file:
            object_dict = json.load(object_file)

        context.dataset_file_aggregate_data = object_dict
        return None

    if context.root_directory:
        dataset_counts_map = {}
        file_reference_directory = get_source_directory(
            api_models.FileReference, context
        )
        file_reference_paths = glob(str(file_reference_directory))
        for file_path in file_reference_paths:
            with open(file_path, "r") as object_file:
                object_dict = json.load(object_file)
                file_reference = api_models.FileReference(**object_dict)
            submission_dataset = str(file_reference.submission_dataset_uuid)
            file_type = file_reference.format
            file_size = file_reference.size_in_bytes
            if submission_dataset not in dataset_counts_map:
                dataset_counts_map[submission_dataset] = {
                    "file_reference_count": 0,
                    "image_count": 0,
                    "file_reference_size_bytes": 0,
                    "file_type_counts": {},
                }
            dataset_counts_map[submission_dataset][
                "file_reference_size_bytes"
            ] += file_size
            dataset_counts_map[submission_dataset]["file_reference_count"] += 1

            if (
                file_type
                not in dataset_counts_map[submission_dataset]["file_type_counts"]
            ):
                dataset_counts_map[submission_dataset]["file_type_counts"][
                    file_type
                ] = 0
            dataset_counts_map[submission_dataset]["file_type_counts"][file_type] += 1

        images_directory = get_source_directory(api_models.Image, context)
        image_paths = glob(str(images_directory))

        for image_path in image_paths:
            with open(image_path, "r") as object_file:
                object_dict = json.load(object_file)
            submission_dataset = object_dict["submission_dataset_uuid"]
            file_type = Path(file_reference.file_path).suffix
            if submission_dataset not in dataset_counts_map:
                dataset_counts_map[submission_dataset] = {
                    "file_reference_count": 0,
                    "image_count": 0,
                    "file_reference_size_bytes": 0,
                    "file_type_counts": {},
                }
            dataset_counts_map[submission_dataset]["image_count"] += 1

        context.dataset_file_aggregate_data = dataset_counts_map
        return None


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
            dataset_uuid, api_client.get_image_linking_dataset, page_size_setting=500
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
    context: StudyCLIContext,
) -> dict[str, List]:
    """
    Returns a dictionary of the form:
    {
        api_models.ImageAcquisitionProtocol: [ api_models.ImageAcquisitionProtocol(IAP1), ... ],
        api_models.BioSample: [ api_models.BioSample(BS1), ... ]
        ...
    }
    """

    detail_classes = [
        api_models.ImageAcquisitionProtocol,
        api_models.BioSample,
        api_models.SpecimenImagingPreparationProtocol,
        api_models.AnnotationMethod,
        api_models.Protocol,
    ]
    detail_fields = {cls: [] for cls in detail_classes}
    attribute_name_type_map = {
        f"{to_snake(cls.__name__)}_uuid": cls for cls in detail_classes
    }

    for attribute in dataset.attribute:
        try:
            attribute_models.DatasetAssociatedUUIDAttribute.model_validate(attribute.model_dump())
        except ValidationError:
            continue
        for uuid in attribute.value[attribute.name]:
            # retrieve_object handles whether to retrieve from file or from api
            api_object = retrieve_object(
                uuid, attribute_name_type_map[attribute.name], context
            )
            detail_fields[attribute_name_type_map[attribute.name]].append(
                api_object
            )

    return detail_fields
