from typing import List, Type
from bia_export.website_export.generic_object_retrieval import (
    retrieve_object_list,
    retrieve_object,
)
from bia_integrator_api import models as api_models
from pydantic import BaseModel
from bia_export.website_export.images.models import (
    Image,
    CreationProcess,
    Specimen,
    ImageCLIContext,
)
from bia_export.website_export.images.retrieve import (
    retrieve_images,
    get_local_img_rep_map,
    retrieve_representations,
)
from bia_export.website_export.website_models import (
    BioSample,
    ImageAcquisitionProtocol,
    Protocol,
    SpecimenImagingPreparationProtocol,
    AnnotationMethod,
)


def transform_images(context: ImageCLIContext) -> Image:
    image_map = {}

    api_images = retrieve_images(context)

    if context.root_directory:
        context.image_to_rep_uuid_map = get_local_img_rep_map(context)

    for api_image in api_images:

        image = transform_image(api_image, context)

        image_map[str(image.uuid)] = image.model_dump(mode="json")

    return image_map


def transform_image(api_image: api_models.Image, context: ImageCLIContext) -> Image:

    api_creation_process = retrieve_object(
        api_image.creation_process_uuid, api_models.CreationProcess, context
    )
    creation_process = transform_creation_process(api_creation_process, context)

    api_img_rep = retrieve_representations(api_image.uuid, context)

    image_dict = api_image.model_dump() | {
        "representation": api_img_rep,
        "creation_process": creation_process,
    }

    return Image(**image_dict)


def transform_creation_process(
    api_creation_process: api_models.CreationProcess, context: ImageCLIContext
) -> CreationProcess:
    website_fields = {}

    if len(api_creation_process.image_acquisition_protocol_uuid) > 0:
        api_image_acquisitions = retrieve_object_list(
            api_creation_process.image_acquisition_protocol_uuid,
            api_models.ImageAcquisitionProtocol,
            context,
        )
        website_fields["acquisition_process"] = transform_details_object_list(
            api_image_acquisitions, ImageAcquisitionProtocol
        )

    if api_creation_process.subject_specimen_uuid:
        api_specimen: api_models.Specimen = retrieve_object(
            api_creation_process.subject_specimen_uuid, api_models.Specimen, context
        )
        website_fields["subject"] = transform_specimen(api_specimen, context)

    if len(api_creation_process.annotation_method_uuid) > 0:
        api_annotation_method = retrieve_object_list(
            api_creation_process.annotation_method_uuid,
            api_models.AnnotationMethod,
            context,
        )
        website_fields["annotation_method"] = transform_details_object_list(
            api_annotation_method, AnnotationMethod
        )

    if len(api_creation_process.protocol_uuid) > 0:
        api_protocol = retrieve_object_list(
            api_creation_process.protocol_uuid, api_models.Protocol, context
        )
        website_fields["protocol"] = transform_details_object_list(
            api_protocol, Protocol
        )

    creation_process_dict = api_creation_process.model_dump() | website_fields
    return CreationProcess(**creation_process_dict)


def transform_specimen(
    api_specimen: api_models.Specimen, context: ImageCLIContext
) -> Specimen:

    api_bio_samples = retrieve_object_list(
        api_specimen.sample_of_uuid, api_models.BioSample, context
    )
    biosamples = []
    for api_bio_sample in api_bio_samples:
        biosamples.append(transform_biosample(api_bio_sample, context))

    api_specimen_imaging_preparation_protocols = retrieve_object_list(
        api_specimen.imaging_preparation_protocol_uuid,
        api_models.SpecimenImagingPreparationProtocol,
        context,
    )

    specimen_dict = api_specimen.model_dump() | {
        "imaging_preparation_protocol": transform_details_object_list(
            api_specimen_imaging_preparation_protocols,
            SpecimenImagingPreparationProtocol,
        ),
        "sample_of": biosamples,
    }
    return Specimen(**specimen_dict)


def transform_biosample(
    api_bio_sample: api_models.BioSample, context: ImageCLIContext
) -> BioSample:
    bio_sample_dict = api_bio_sample.model_dump()
    if api_bio_sample.growth_protocol_uuid:
        bio_sample_dict["growth_protocol"] = retrieve_object(
            api_bio_sample.growth_protocol_uuid, api_models.Protocol, context
        )
    bio_sample_dict["default_open"] = True
    return BioSample(**bio_sample_dict)


def transform_details_object_list(
    api_object_list: List[BaseModel], website_class: Type[BaseModel]
):
    obj_list = []
    for api_obj in api_object_list:
        obj_dict = api_obj.model_dump() | {"default_open": True}
        obj_list.append(website_class(**obj_dict))
    return obj_list
