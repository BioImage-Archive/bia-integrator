from uuid import UUID
from bia_shared_datamodels import uuid_creation, attribute_models
from bia_shared_datamodels.semantic_models import Provenance
from bia_shared_datamodels.package_specific_uuid_creation import shared


def create_dataset_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    unique_string = f"{ro_crate_id}"
    return (
        uuid_creation.create_dataset_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_bio_sample_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    unique_string = f"{ro_crate_id}"
    return (
        uuid_creation.create_bio_sample_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_protocol_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    unique_string = f"{ro_crate_id}"
    return (
        uuid_creation.create_protocol_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_annotation_method_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    unique_string = f"{ro_crate_id}"
    return (
        uuid_creation.create_annotation_method_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_specimen_imaging_preparation_protocol_uuid(
    study_uuid: str, ro_crate_id: str
):
    unique_string = f"{ro_crate_id}"
    return (
        uuid_creation.create_specimen_imaging_preparation_protocol_uuid(
            study_uuid=study_uuid, unique_string=f"{ro_crate_id}"
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_image_acquisition_protocol_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    unique_string = f"{ro_crate_id}"
    return (
        uuid_creation.create_image_acquisition_protocol_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )
