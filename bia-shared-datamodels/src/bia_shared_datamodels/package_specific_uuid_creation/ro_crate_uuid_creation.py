from urllib.parse import unquote
from uuid import UUID

from bia_shared_datamodels import attribute_models, uuid_creation
from bia_shared_datamodels.package_specific_uuid_creation import shared
from bia_shared_datamodels.semantic_models import Provenance


def unencode_relative_id(ro_crate_id: str):
    unique_string = unquote(str(ro_crate_id).removeprefix("#").removeprefix("_:"))
    return unique_string


def create_dataset_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUniqueInputAttribute]:
    # unqote is used to transform %20 that may be present in the uri id into spaces
    unique_string = unencode_relative_id(ro_crate_id).removesuffix("/")
    return (
        uuid_creation.create_dataset_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_bio_sample_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUniqueInputAttribute]:
    # _:_ can be present for
    unique_string = unencode_relative_id(str(ro_crate_id).removeprefix("_:_"))
    return (
        uuid_creation.create_bio_sample_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_protocol_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUniqueInputAttribute]:
    unique_string = unencode_relative_id(ro_crate_id)
    return (
        uuid_creation.create_protocol_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_annotation_method_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUniqueInputAttribute]:
    unique_string = unencode_relative_id(ro_crate_id)
    return (
        uuid_creation.create_annotation_method_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_specimen_imaging_preparation_protocol_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUniqueInputAttribute]:
    unique_string = unencode_relative_id(ro_crate_id)
    return (
        uuid_creation.create_specimen_imaging_preparation_protocol_uuid(
            study_uuid=study_uuid, unique_string=f"{ro_crate_id}"
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_image_acquisition_protocol_uuid(
    study_uuid: str, ro_crate_id: str
) -> tuple[UUID, attribute_models.DocumentUUIDUniqueInputAttribute]:
    unique_string = unencode_relative_id(ro_crate_id)
    return (
        uuid_creation.create_image_acquisition_protocol_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_specimen_uuid(
    study_uuid: str,
    ro_crate_id: str,
) -> tuple[UUID, attribute_models.DocumentUUIDUniqueInputAttribute]:
    """
    This is for creating a specimen object assuming it was included in the ro-crate.
    """
    unique_string = unencode_relative_id(ro_crate_id)
    return (
        uuid_creation.create_specimen_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )


def create_creation_process_uuid(
    study_uuid: str,
    ro_crate_id: str,
) -> tuple[UUID, attribute_models.DocumentUUIDUniqueInputAttribute]:
    """
    This is for creating a creation process object assuming it was included in the ro-crate.
    """
    unique_string = unencode_relative_id(ro_crate_id)
    return (
        uuid_creation.create_creation_process_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        shared.create_unique_str_attribute(unique_string, Provenance.bia_ingest),
    )
