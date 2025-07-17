from uuid import UUID
from bia_shared_datamodels import uuid_creation, attribute_models
from bia_shared_datamodels.semantic_models import Provenance
from typing import Optional
from bia_shared_datamodels.package_specific_uuid_creation import shared


def create_dataset_uuid(
    study_uuid: str, biostudies_section_accno: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    unique_string = f"{biostudies_section_accno}"
    return (
        uuid_creation.create_dataset_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_dataset_uuid_for_default_bsst_template_submissions(
    study_uuid: str,
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    """
    Used when a biostudies submission has no dataset and has file references attached to the study directly.
    """
    unique_string = f"Default template. No Study Components"
    return (
        uuid_creation.create_dataset_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_bio_sample_uuid(
    study_uuid: str, biostudies_section_accno: str, growth_protocol_uuid: Optional[str]
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    if growth_protocol_uuid:
        unique_string = f"{biostudies_section_accno} {growth_protocol_uuid}"
    else:
        unique_string = f"{biostudies_section_accno}"

    return (
        uuid_creation.create_bio_sample_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_protocol_uuid(
    study_uuid: str, biostudies_section_accno: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    unique_string = f"{biostudies_section_accno}"
    return (
        uuid_creation.create_protocol_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_annotation_method_uuid(
    study_uuid: str, biostudies_section_accno: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    unique_string = f"{biostudies_section_accno}"
    return (
        uuid_creation.create_annotation_method_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_specimen_imaging_preparation_protocol_uuid(
    study_uuid: str, biostudies_section_accno: str
):
    unique_string = f"{biostudies_section_accno}"

    return (
        uuid_creation.create_specimen_imaging_preparation_protocol_uuid(
            study_uuid=study_uuid, unique_string=f"{biostudies_section_accno}"
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_image_acquisition_protocol_uuid(
    study_uuid: str, biostudies_section_accno: str
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    unique_string = f"{biostudies_section_accno}"
    return (
        uuid_creation.create_image_acquisition_protocol_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )
