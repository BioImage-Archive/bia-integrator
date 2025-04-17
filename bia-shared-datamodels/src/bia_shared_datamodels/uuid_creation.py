from uuid import UUID
import hashlib
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


def create_dataset_uuid(study_uuid: UUID, unique_string: str) -> UUID:
    return __list_to_uuid([study_uuid, Dataset.__name__, unique_string])


def create_file_reference_uuid(study_uuid: UUID, unique_string: str) -> UUID:
    return __list_to_uuid([study_uuid, FileReference.__name__, unique_string])


def create_image_uuid(study_uuid: UUID, unique_string: str) -> UUID:
    return __list_to_uuid([study_uuid, Image.__name__, unique_string])


def create_image_representation_uuid(study_uuid: UUID, unique_string: str) -> UUID:
    return __list_to_uuid([study_uuid, ImageRepresentation.__name__, unique_string])


def create_creation_process_uuid(study_uuid: UUID, unique_string: str) -> UUID:
    return __list_to_uuid([study_uuid, CreationProcess.__name__, unique_string])


def create_specimen_uuid(study_uuid: UUID, unique_string: str) -> UUID:
    return __list_to_uuid([study_uuid, Specimen.__name__, unique_string])


def create_protocol_uuid(study_uuid: UUID, unique_string: str) -> UUID:
    return __list_to_uuid([study_uuid, Protocol.__name__, unique_string])


def create_annotation_method_uuid(study_uuid: UUID, unique_string: str) -> UUID:
    return __list_to_uuid([study_uuid, AnnotationMethod.__name__, unique_string])


def create_image_acquisition_protocol_uuid(
    study_uuid: UUID, unique_string: str
) -> UUID:
    return __list_to_uuid(
        [study_uuid, ImageAcquisitionProtocol.__name__, unique_string]
    )


def create_specimen_imaging_preparation_protocol_uuid(
    study_uuid: UUID, unique_string: str
) -> UUID:
    return __list_to_uuid(
        [study_uuid, SpecimenImagingPreparationProtocol.__name__, unique_string]
    )


def create_bio_sample_uuid(study_uuid: UUID, unique_string: str) -> UUID:
    return __list_to_uuid([study_uuid, BioSample.__name__, unique_string])
