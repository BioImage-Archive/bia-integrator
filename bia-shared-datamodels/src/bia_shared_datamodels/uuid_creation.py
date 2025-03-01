from uuid import UUID
import hashlib
from pathlib import Path
from typing import Optional
from .bia_data_model import (
    Dataset,
    FileReference,
    Image,
    ImageRepresentation,
    CreationProcess,
    Specimen,
    Protocol,
    AnnotationMethod,
    ImageAcquisitionProtocol,
    SpecimenImagingPreparationProtocol,
    BioSample,
)


def __list_to_uuid(list_of_fields: list) -> UUID:
    """
    Create uuid from a list of values.
    Note this function is not intended for use for the creation of BIA UUIDS outside of the functions defined below.
    """
    seed = "".join([str(value) for value in list_of_fields])
    hexdigest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    return UUID(version=4, hex=hexdigest)


def create_study_uuid(accession_id: str) -> UUID:
    return __list_to_uuid([accession_id])


def create_dataset_uuid(title_id: str, study_uuid: UUID) -> UUID:
    return __list_to_uuid([title_id, study_uuid, Dataset.__name__])


def create_file_reference_uuid(file_path: Path, study_uuid: UUID) -> UUID:
    return __list_to_uuid([file_path, study_uuid, FileReference.__name__])


# These should be based on the file reference uuids, which already factor in the study uuid
def create_image_uuid(file_reference_uuid_list: list[UUID]) -> UUID:
    uuid_field_list = [Image.__name__]
    [uuid_field_list.append(uuid) for uuid in file_reference_uuid_list]
    return __list_to_uuid(uuid_field_list)


# Image representations are unique to use type. A new use type will need to
# be created if distinct representations of same image in same format are required
def create_image_representation_uuid(image_uuid: UUID, image_format: str, use_type: str) -> UUID:
    return __list_to_uuid([image_uuid, image_format, use_type, ImageRepresentation.__name__])


def create_creation_process_uuid(image_uuid: UUID) -> UUID:
    return __list_to_uuid([image_uuid, CreationProcess.__name__])


def create_specimen_uuid(image_uuid: UUID) -> UUID:
    return __list_to_uuid([image_uuid, Specimen.__name__])


def create_protocol_uuid(title_id: str, study_uuid: UUID) -> UUID:
    return __list_to_uuid([title_id, study_uuid, Protocol.__name__])


def create_annotation_method_uuid(title_id: str, study_uuid: UUID) -> UUID:
    return __list_to_uuid([title_id, study_uuid, AnnotationMethod.__name__])


def create_image_acquisition_protocol_uuid(title_id: str, study_uuid: UUID) -> UUID:
    return __list_to_uuid([title_id, study_uuid, ImageAcquisitionProtocol.__name__])


def create_specimen_imaging_preparation_protocol_uuid(
    title_id: str, study_uuid: UUID
) -> UUID:
    return __list_to_uuid(
        [title_id, study_uuid, SpecimenImagingPreparationProtocol.__name__]
    )


def create_bio_sample_uuid(
    title_id: str, study_uuid: UUID, growth_protocol_uuid: Optional[UUID] = None
) -> UUID:
    return __list_to_uuid(
        [title_id, study_uuid, growth_protocol_uuid, BioSample.__name__]
    )
