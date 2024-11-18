from pydantic import BaseModel
from typing import List, Type
from bia_export.website_export.studies.models import (
    Dataset,
    Study,
    StudyCLIContext,
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
)
from bia_integrator_api import models as api_models
import logging

logger = logging.getLogger("__main__." + __name__)


def transform_study(context: StudyCLIContext) -> Study:

    api_study = retrieve_study(context)
    study_dict = api_study.model_dump()

    # Collect file list information prior to creating eid if reading locally to avoid reading them multiple times.
    # TODO: make transform_study api/local independent: only retreive functions should have to worry about this.
    if context.root_directory:
        context.dataset_file_aggregate_data = aggregate_file_list_data(context)

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

    detail_map = {
        "acquisition_process": {
            "association_field": "image_acquisition",
            "bia_type": api_models.ImageAcquisitionProtocol,
            "website_type": ImageAcquisitionProtocol,
        },
        "biological_entity": {
            "association_field": "biosample",
            "bia_type": api_models.BioSample,
            "website_type": BioSample,
        },
        "specimen_imaging_preparation_protocol": {
            "association_field": "specimen",
            "bia_type": api_models.SpecimenImagingPreparationProtocol,
            "website_type": SpecimenImagingPreparationProtocol,
        },
    }

    api_details = retrieve_detail_objects(dataset, detail_map, context)

    detail_fields: dict[str, List[BaseModel]] = {}
    for field, object_list in api_details.items():
        detail_fields[field] = []
        for api_object in object_list:
            detail = transform_detail_object(
                api_object,
                detail_map[field]["website_type"],
                context,
            )
            detail_fields[field].append(detail)

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
    detail = target_type(**detail_dict)
    return detail
