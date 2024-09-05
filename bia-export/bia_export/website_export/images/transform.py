from typing import List, Type
from bia_shared_datamodels import bia_data_model
from pydantic import BaseModel
from bia_export.website_export.images.models import (
    ExperimentallyCapturedImage,
    Specimen,
    ImageCLIContext,
)
from bia_export.website_export.images.retrieve import (
    retrieve_images,
    retrieve_specimen,
    retrieve_object_list,
    get_local_img_rep_map,
    retrieve_representations,
)
from bia_export.website_export.website_models import (
    BioSample,
    ImageAcquisition,
    SpecimenGrowthProtocol,
    SpecimenImagingPreparationProtocol,
)


def transform_ec_images(context: ImageCLIContext) -> ExperimentallyCapturedImage:
    eci_map = {}

    api_images = retrieve_images(context)

    if context.root_directory:
        context.image_to_rep_uuid_map = get_local_img_rep_map(context)

    for api_image in api_images:

        image = transform_image(api_image, context)

        eci_map[str(image.uuid)] = image.model_dump(mode="json")

    return eci_map


def transform_image(
    api_image: bia_data_model.ExperimentallyCapturedImage, context: ImageCLIContext
) -> ExperimentallyCapturedImage:
    website_fields = {}
    api_image_acquisitions = retrieve_object_list(
        api_image.acquisition_process_uuid, bia_data_model.ImageAcquisition, context
    )

    website_fields["acquisition_process"] = transform_details_object_list(
        api_image_acquisitions, ImageAcquisition
    )

    api_specimen = retrieve_specimen(api_image.subject_uuid, context)
    api_biosamples = retrieve_object_list(
        api_specimen.sample_of_uuid, bia_data_model.BioSample, context
    )
    api_specimen_growth_protocols = retrieve_object_list(
        api_specimen.growth_protocol_uuid,
        bia_data_model.SpecimenGrowthProtocol,
        context,
    )
    api_specimen_imaging_preparation_protocols = retrieve_object_list(
        api_specimen.imaging_preparation_protocol_uuid,
        bia_data_model.SpecimenImagingPreparationProtocol,
        context,
    )

    specimen_dict = api_specimen.model_dump() | {
        "imaging_preparation_protocol": transform_details_object_list(
            api_specimen_imaging_preparation_protocols,
            SpecimenImagingPreparationProtocol,
        ),
        "sample_of": transform_details_object_list(api_biosamples, BioSample),
        "growth_protocol": transform_details_object_list(
            api_specimen_growth_protocols, SpecimenGrowthProtocol
        ),
    }
    website_fields["subject"] = Specimen(**specimen_dict)

    api_img_rep = retrieve_representations(api_image.uuid, context)

    image_dict = (
        api_image.model_dump() | website_fields | {"representation": api_img_rep}
    )

    return ExperimentallyCapturedImage(**image_dict)


def transform_details_object_list(
    api_object_list: List[BaseModel], website_class: Type[BaseModel]
):
    obj_list = []
    for api_obj in api_object_list:
        obj_dict = api_obj.model_dump() | {"default_open": True}
        obj_list.append(website_class(**obj_dict))
    return obj_list
