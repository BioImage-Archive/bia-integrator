from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import uuid_creation
import bia_integrator_api.models as APIModels
import bia_shared_datamodels.ro_crate_models as ROCrateModels
import bia_shared_datamodels.attribute_models as AttributeModels
import logging
from bia_shared_datamodels.package_specific_uuid_creation.ro_crate_uuid_creation import (
    create_dataset_uuid,
)

logger = logging.getLogger("__main__." + __name__)


def create_api_dataset(
    crate_objects_by_id: dict[str, ROCrateModel], study_uuid: str
) -> list[APIModels.Dataset]:
    ro_crate_datasets = (
        obj
        for obj in crate_objects_by_id.values()
        if isinstance(obj, ROCrateModels.Dataset)
    )

    dataset_list = []
    for dataset in ro_crate_datasets:
        dataset_list.append(convert_dataset(dataset, study_uuid))

    return dataset_list


def convert_dataset(
    ro_crate_dataset: ROCrateModels.Dataset,
    study_uuid: str,
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

    dataset = {
        "uuid": str(uuid),
        "submitted_in_study_uuid": study_uuid,
        "title": title,
        "description": ro_crate_dataset.description,
        "version": 0,
        "example_image_uri": [],
        "object_creator": APIModels.Provenance.BIA_INGEST,
        "additional_metadata": additional_metadata,
        "analysis_method": [],
        "correlation_method": [],
    }

    return APIModels.Dataset(**dataset)


def dataset_attribute_links_with_uuids(
    ro_crate_dataset: ROCrateModels.Dataset, study_uuid: str
) -> list[dict]:
    additional_metadata = []

    field_attribute_pairs = [
        ("associatedImageAcquisitionProtocol", "image_acquisition_protocol_uuid"),
        (
            "associatedSpecimenImagingPreparationProtocol",
            "specimen_imaging_preparation_protocol_uuid",
        ),
        ("associatedBiologicalEntity", "bio_sample_uuid"),
        ("associatedAnnotationMethod", "annotation_method_uuid"),
        ("associatedProtocol", "protocol_uuid"),
    ]

    for field, attribute_name in field_attribute_pairs:
        if len(getattr(ro_crate_dataset, field)) > 0:
            uuids = [
                str(uuid_creation.create_annotation_method_uuid(study_uuid, x.id))
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
