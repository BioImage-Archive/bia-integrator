import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import bia_shared_datamodels.attribute_models as AttributeModels
import logging

from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_dataset_uuid,
    create_bio_sample_uuid,
    create_protocol_uuid,
    create_image_acquisition_protocol_uuid,
    create_annotation_method_uuid,
    create_specimen_imaging_preparation_protocol_uuid,
)

logger = logging.getLogger("__main__." + __name__)


def create_api_dataset(
    crate_objects_by_id: dict[str, ROCrateModel], study_uuid: str
) -> list[APIModels.Dataset]:
    ro_crate_datasets = []
    ro_crate_image_analysis_methods = []
    ro_crate_image_correlation_methods = []

    for obj in crate_objects_by_id.values():
        if isinstance(obj, ROCrateModels.Dataset):
            ro_crate_datasets.append(obj)
        elif isinstance(obj, ROCrateModels.ImageAnalysisMethod):
            ro_crate_image_analysis_methods.append(obj)
        elif isinstance(obj, ROCrateModels.ImageCorrelationMethod):
            ro_crate_image_correlation_methods.append(obj)

    api_image_analysis_methods = {}
    api_image_correlation_methods = {}

    for image_analysis_method in ro_crate_image_analysis_methods:
        api_image_analysis_methods[image_analysis_method.id] = (
            convert_image_analysis_method(image_analysis_method)
        )

    for image_correlation_method in ro_crate_image_correlation_methods:
        api_image_correlation_methods[image_correlation_method.id] = (
            convert_image_correlation_method(image_correlation_method)
        )

    dataset_list = []
    for dataset in ro_crate_datasets:
        dataset_list.append(
            convert_dataset(
                dataset,
                study_uuid,
                api_image_analysis_methods,
                api_image_correlation_methods,
            )
        )

    return dataset_list


def convert_dataset(
    ro_crate_dataset: ROCrateModels.Dataset,
    study_uuid: str,
    api_image_analysis_methods: dict[str, APIModels.ImageAnalysisMethod],
    api_image_correlation_methods: dict[str, APIModels.ImageCorrelationMethod],
) -> APIModels.Dataset:

    title = None
    if ro_crate_dataset.title:
        title = ro_crate_dataset.title
    elif ro_crate_dataset.id:
        title = ro_crate_dataset.id

    uuid, uuid_attribute = create_dataset_uuid(study_uuid, ro_crate_dataset.id)

    additional_metadata = dataset_attribute_links_with_uuids(
        ro_crate_dataset, study_uuid
    )
    additional_metadata.append(uuid_attribute.model_dump())

    analysis_methods = [
        api_image_analysis_methods[reference.id]
        for reference in ro_crate_dataset.associatedImageAnalysisMethod
    ]

    correlation_methods = [
        api_image_correlation_methods[reference.id]
        for reference in ro_crate_dataset.associatedImageCorrelationMethod
    ]

    dataset = {
        "uuid": str(uuid),
        "submitted_in_study_uuid": study_uuid,
        "title": title,
        "description": ro_crate_dataset.description,
        "version": 0,
        "example_image_uri": [],
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": additional_metadata,
        "analysis_method": analysis_methods,
        "correlation_method": correlation_methods,
    }

    return APIModels.Dataset(**dataset)


def dataset_attribute_links_with_uuids(
    ro_crate_dataset: ROCrateModels.Dataset, study_uuid: str
) -> list[dict]:
    additional_metadata = []

    field_attribute_map = [
        (
            "associatedImageAcquisitionProtocol",
            "image_acquisition_protocol_uuid",
            create_image_acquisition_protocol_uuid,
        ),
        (
            "associatedSpecimenImagingPreparationProtocol",
            "specimen_imaging_preparation_protocol_uuid",
            create_specimen_imaging_preparation_protocol_uuid,
        ),
        (
            "associatedAnnotationMethod",
            "annotation_method_uuid",
            create_annotation_method_uuid,
        ),
        ("associatedBiologicalEntity", "bio_sample_uuid", create_bio_sample_uuid),
        ("associatedProtocol", "protocol_uuid", create_protocol_uuid),
    ]

    for field, attribute_name, uuid_func in field_attribute_map:
        if len(getattr(ro_crate_dataset, field)) > 0:
            uuids = [
                str(uuid_func(study_uuid, x.id)[0])
                for x in getattr(ro_crate_dataset, field)
            ]
            additional_metadata.append(
                AttributeModels.DatasetAssociatedUUIDAttribute(
                    provenance=APIModels.Provenance.BIA_INGEST,
                    name=attribute_name,
                    value={attribute_name: uuids},
                ).model_dump()
            )

    return additional_metadata


def convert_image_analysis_method(
    ro_crate_image_analysis_method: ROCrateModels.ImageAnalysisMethod,
) -> APIModels.ImageAnalysisMethod:
    image_analysis_method = {
        "title": ro_crate_image_analysis_method.title,
        "protocol_description": ro_crate_image_analysis_method.protocolDescription,
        "features_analysed": ro_crate_image_analysis_method.featuresAnalysed,
        "additional_metadata": [],
    }
    return APIModels.ImageAnalysisMethod(**image_analysis_method)


def convert_image_correlation_method(
    ro_crate_image_correlation_method: ROCrateModels.ImageCorrelationMethod,
) -> APIModels.ImageCorrelationMethod:
    image_correlation_method = {
        "title": ro_crate_image_correlation_method.title,
        "protocol_description": ro_crate_image_correlation_method.protocolDescription,
        "fiducials_used": ro_crate_image_correlation_method.fiducialsUsed,
        "transformation_matrix": ro_crate_image_correlation_method.transformationMatrix,
        "additional_metadata": [],
    }
    return APIModels.ImageCorrelationMethod(**image_correlation_method)
