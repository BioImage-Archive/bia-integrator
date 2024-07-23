from __future__ import annotations

from . import semantic_models
from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from enum import Enum


class DocumentMixin(BaseModel):
    uuid: UUID = Field(
        description="""Unique ID (across the BIA database) used to refer to and identify a document."""
    )


class UserIdentifiedObject(BaseModel):
    title_id: str = Field(
        description="""User provided title, which is unqiue within a submission, used to identify a part of a submission."""
    )


class Study(
    semantic_models.Study,
    DocumentMixin,
):
    author: List[semantic_models.Contributor] = Field(min_length=1)


class FileReference(
    semantic_models.FileReference,
    DocumentMixin,
):
    submission_dataset_uuid: UUID = Field()


class ImageRepresentation(
    semantic_models.ImageRepresentation,
    DocumentMixin,
):
    # We may want to store the FileReference -> Image(Represenation) rather than in the original_file_reference_uuid
    original_file_reference_uuid: Optional[List[UUID]] = Field()
    representation_of_uuid: UUID = Field()


class ExperimentalImagingDataset(
    semantic_models.ExperimentalImagingDataset,
    DocumentMixin,
    UserIdentifiedObject,
):
    submitted_in_study_uuid: UUID = Field()


class Specimen(semantic_models.Specimen, DocumentMixin):
    imaging_preparation_protocol_uuid: List[UUID] = Field(min_length=1)
    sample_of_uuid: List[UUID] = Field(min_length=1)
    growth_protocol_uuid: List[UUID] = Field()


class ExperimentallyCapturedImage(
    semantic_models.ExperimentallyCapturedImage,
    DocumentMixin,
):
    acquisition_process_uuid: List[UUID] = Field()
    submission_dataset_uuid: UUID = Field()
    subject_uuid: UUID = Field()

class ImageAcquisition(
    semantic_models.ImageAcquisition,
    DocumentMixin,
    UserIdentifiedObject,
):
    pass


class SpecimenImagingPrepartionProtocol(
    semantic_models.SpecimenImagingPrepartionProtocol,
    DocumentMixin,
    UserIdentifiedObject,
):
    pass


class SpecimenGrowthProtocol(
    semantic_models.SpecimenGrowthProtocol,
    DocumentMixin,
    UserIdentifiedObject,
):
    pass


class BioSample(
    semantic_models.BioSample,
    DocumentMixin,
    UserIdentifiedObject,
):
    pass


class ImageAnnotationDataset(
    semantic_models.ImageAnnotationDataset,
    DocumentMixin,
    UserIdentifiedObject,
):
    submitted_in_study_uuid: UUID = Field()


class AnnotationFileReference(
    semantic_models.AnnotationFileReference,
    DocumentMixin,
):
    submission_dataset_uuid: UUID = Field()
    source_image_uuid: List[UUID] = Field()
    creation_process_uuid: List[UUID] = Field()


class DerivedImage(
    semantic_models.DerivedImage,
    DocumentMixin,
):
    source_image_uuid: List[UUID] = Field()
    submission_dataset_uuid: UUID = Field()
    creation_process_uuid: List[UUID] = Field()


class AnnotationMethod(
    semantic_models.AnnotationMethod,
    DocumentMixin,
    UserIdentifiedObject,
):
    pass

