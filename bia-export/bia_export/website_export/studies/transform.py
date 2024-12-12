from pydantic import BaseModel
from typing import List, Type
from bia_export.website_export.studies.models import (
    Dataset,
    Study,
    StudyCLIContext,
    CacheUse
)
from bia_export.website_export.studies.retrieve import (
    retrieve_study,
    retrieve_dataset_images,
    aggregate_file_list_data,
    retrieve_aggregation_fields,
    retrieve_detail_objects,
    retrieve_datasets,
)
from bia_export.website_export.website_models import (
    BioSample,
    DetailSection,
    ImageAcquisitionProtocol,
    Protocol,
    SpecimenImagingPreparationProtocol,
    AnnotationMethod,
)
from bia_export.website_export.generic_object_retrieval import retrieve_object
from bia_integrator_api import models as api_models
import logging

logger = logging.getLogger("__main__." + __name__)


def transform_study(context: StudyCLIContext) -> Study:

    api_study = retrieve_study(context)
    study_dict = api_study.model_dump()

    # Collect file list information prior to creating eid if reading locally to avoid reading them multiple times.
    # TODO: make transform_study api/local independent: only retreive functions should have to worry about this.
    if context.root_directory or context.cache_use == CacheUse.READ_CACHE:
        aggregate_file_list_data(context)

    study_dict["dataset"] = transform_datasets(context)

    study = Study(**study_dict)
    return study


def transform_datasets(
    context: StudyCLIContext,
) -> List[Dataset]:
    api_datasets = retrieve_datasets(context)

    dataset_list = []
    for api_dataset in api_datasets:
        dataset_list.append(transform_dataset(api_dataset, context))

    return dataset_list


def transform_dataset(
    api_dataset: api_models.Dataset,
    context: StudyCLIContext,
) -> Dataset:

    dataset_dict = api_dataset.model_dump()

    # Details include Biosample, and various Protocols
    dataset_dict = dataset_dict | transform_dataset_detail_objects(api_dataset, context)

    dataset_dict = dataset_dict | retrieve_aggregation_fields(api_dataset, context)

    dataset_api_images = retrieve_dataset_images(
        api_dataset.uuid, api_models.Image, context
    )
    dataset_dict = dataset_dict | {"image": dataset_api_images}

    dataset = Dataset(**dataset_dict)
    return dataset


def transform_dataset_detail_objects(
    dataset: api_models.Dataset, context: StudyCLIContext
):

    dataset_detail_class_map = {
        api_models.ImageAcquisitionProtocol: ImageAcquisitionProtocol,
        api_models.SpecimenImagingPreparationProtocol: SpecimenImagingPreparationProtocol,
        api_models.BioSample: BioSample,
        api_models.Protocol: Protocol,
        api_models.AnnotationMethod: AnnotationMethod,
    }

    dataset_field = {
        ImageAcquisitionProtocol: "acquisition_process",
        SpecimenImagingPreparationProtocol: "specimen_imaging_preparation_protocol",
        BioSample: "biological_entity",
        Protocol: "other_creation_process",
        AnnotationMethod: "annotation_process",
    }

    api_details = retrieve_detail_objects(dataset, context)

    detail_fields: dict[str, List[BaseModel]] = {}
    for object_type, object_list in api_details.items():
        if len(object_list) > 0:
            website_class = dataset_detail_class_map[object_type]
            detail_fields[dataset_field[website_class]] = []
            for api_object in object_list:
                detail = transform_detail_object(
                    api_object,
                    website_class,
                    context,
                )
                detail_fields[dataset_field[website_class]].append(detail)

    return detail_fields


def transform_detail_object(
    detail_object: BaseModel,
    target_type: Type[DetailSection],
    context: StudyCLIContext,
):
    detail_dict = detail_object.model_dump()
    if detail_dict["uuid"] not in context.displayed_dataset_detail[target_type]:
        detail_dict["default_open"] = True
        context.displayed_dataset_detail[target_type].add(detail_dict["uuid"])
    else:
        detail_dict["default_open"] = False
    if target_type == BioSample and detail_dict["growth_protocol_uuid"]:
        api_growth_protocol = retrieve_object(
            detail_dict["growth_protocol_uuid"], api_models.Protocol, context
        )
        detail_dict["growth_protocol"] = api_growth_protocol

    detail = target_type(**detail_dict)
    return detail
