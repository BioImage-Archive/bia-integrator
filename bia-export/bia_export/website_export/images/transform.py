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

    physical_sizes = transform_physical_size_xyz_from_image_rep(api_img_rep)

    accession_id = context.accession_id

    image_dict = api_image.model_dump() | {
        "representation": api_img_rep,
        "creation_process": creation_process,
        **physical_sizes,
        "accession_id": accession_id,
    }

    return Image(**image_dict)


def transform_creation_process(
    api_creation_process: api_models.CreationProcess, context: ImageCLIContext
) -> CreationProcess:
    website_fields = {}

    if (
        api_creation_process.image_acquisition_protocol_uuid
        and len(api_creation_process.image_acquisition_protocol_uuid) > 0
    ):
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

    if (
        api_creation_process.annotation_method_uuid
        and len(api_creation_process.annotation_method_uuid) > 0
    ):
        api_annotation_method = retrieve_object_list(
            api_creation_process.annotation_method_uuid,
            api_models.AnnotationMethod,
            context,
        )
        website_fields["annotation_method"] = transform_details_object_list(
            api_annotation_method, AnnotationMethod
        )

    if (
        api_creation_process.protocol_uuid
        and len(api_creation_process.protocol_uuid) > 0
    ):
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


def transform_physical_size_xyz_from_image_rep(
    api_image_reps: list[api_models.ImageRepresentation],
) -> dict:
    """
    Calculates the total sample physical size from
    the first OME.ZARR image rep by multiplying the
    pixel size (size_x,size_y,size_z) with repective
    the voxel_physical_size.
    """
    img_rep = [
        img_rep for img_rep in api_image_reps if img_rep.image_format == ".ome.zarr"
    ]

    if len(img_rep) == 0:
        return {
            "total_physical_size_x": None,
            "total_physical_size_y": None,
            "total_physical_size_z": None,
        }
    # TO-DO: Maybe calculate/check which rep has the voxels sizes?
    img_rep = img_rep[0]

    physical_size = {}
    physical_size["total_physical_size_x"] = calculate_total_physical_size(
        img_rep.size_x, img_rep.voxel_physical_size_x
    )
    physical_size["total_physical_size_y"] = calculate_total_physical_size(
        img_rep.size_y, img_rep.voxel_physical_size_y
    )
    physical_size["total_physical_size_z"] = calculate_total_physical_size(
        img_rep.size_z, img_rep.voxel_physical_size_z
    )

    return physical_size


def calculate_total_physical_size(pixels, voxel_physical_size) -> float | None:
    try:
        return (
            None
            if voxel_physical_size == 1
            else float(pixels) * float(voxel_physical_size)
        )
    except:
        return None
