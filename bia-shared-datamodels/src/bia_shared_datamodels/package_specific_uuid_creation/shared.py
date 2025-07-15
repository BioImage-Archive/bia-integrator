from uuid import UUID
from bia_shared_datamodels import uuid_creation, attribute_models
from bia_shared_datamodels.semantic_models import Provenance


def create_study_uuid(
    accession_id: str,
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    return (
        uuid_creation.create_study_uuid(accession_id=accession_id),
        create_unique_str_attribute(accession_id, Provenance.bia_ingest),
    )


def create_file_reference_uuid(
    study_uuid: str,
    file_path: str,
    file_size_in_bytes: str,
    provenance: Provenance = Provenance.bia_ingest,
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    unique_string = f"{file_path}{file_size_in_bytes}"
    return (
        uuid_creation.create_file_reference_uuid(
            study_uuid=study_uuid, unique_string=unique_string
        ),
        create_unique_str_attribute(unique_string, provenance),
    )


def create_image_uuid(
    study_uuid: str,
    file_reference_uuids: list[str],
    provenance: Provenance,
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    uuid_unique_input = " ".join([str(u) for u in sorted(file_reference_uuids)])
    return (
        uuid_creation.create_image_uuid(
            study_uuid=study_uuid, uuid_unique_input=uuid_unique_input
        ),
        create_unique_str_attribute(uuid_unique_input, provenance),
    )


def create_annotation_data_uuid(
    study_uuid: str,
    file_reference_uuids: list[str],
    provenance: Provenance,
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    uuid_unique_input = " ".join([str(u) for u in sorted(file_reference_uuids)])
    return (
        uuid_creation.create_annotation_data_uuid(
            study_uuid=study_uuid, uuid_unique_input=uuid_unique_input
        ),
        create_unique_str_attribute(uuid_unique_input, provenance),
    )


def create_specimen_uuid(
    study_uuid: str,
    image_uuid: str,
    provenance: Provenance,
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    """
    This is for creating a specimen object assuming it is unqiue to an image, and no id has been provided.
    If multiple images were created using the same specimen explicitly some other uuid creation may be more appropriate.
    """
    uuid_unique_input = f"{image_uuid}"
    return (
        uuid_creation.create_specimen_uuid(
            accession_id=study_uuid, uuid_unique_input=uuid_unique_input
        ),
        uuid_unique_input,
    )


def create_creation_process_uuid(
    study_uuid: str,
    image_uuid: str,
    provenance: Provenance,
) -> tuple[UUID, attribute_models.DocumentUUIDUinqueInputAttribute]:
    """
    This is for creating a creation process object assuming it is unqiue to an image, and no id has been provided.
    If multiple images were created as the output of the same creation process some other uuid creation may be more appropriate.
    """
    unique_string = f"{image_uuid}"
    return (
        uuid_creation.create_creation_process_uuid(
            study_uuid=study_uuid,
        ),
        unique_string,
    )


def create_unique_str_attribute(
    unique_string: str, provenence: Provenance
) -> attribute_models.DocumentUUIDUinqueInputAttribute:
    return attribute_models.DocumentUUIDUinqueInputAttribute(
        provenance=provenence,
        name="uuid_unique_input",
        value={"uuid_unique_input": unique_string},
    )
