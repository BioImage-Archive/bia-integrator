from __future__ import annotations

import semantic_models
from pydantic import BaseModel, Field, AnyUrl, conlist
from typing import List, Optional, Union
from uuid import UUID

from pydantic_core import Url


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
    experimental_imaging_component: List[UUID] = Field()
    annotation_component: List[UUID] = Field()


class FileReference(
    semantic_models.FileReference,
    DocumentMixin,
):
    submission_dataset: UUID = Field()


class ImageRepresentation(
    semantic_models.ImageRepresentation,
    DocumentMixin,
):
    original_file_reference: Optional[List[UUID]] = Field()


class ExperimentalImagingDataset(
    semantic_models.ExperimentalImagingDataset,
    DocumentMixin,
    UserIdentifiedObject,
):
    image: List[UUID] = Field()
    file: List[UUID] = Field()
    submitted_in_study: UUID = Field()
    specimen_preparation_method: List[UUID] = Field()
    acquisition_method: List[UUID] = Field()
    biological_entity: List[UUID] = Field()
    # we include image analysis and correlation


class Specimen(semantic_models.Specimen):
    preparation_method: conlist(item_type=UUID, min_length=1) = Field()
    sample_of: conlist(item_type=UUID, min_length=1) = Field()


class ExperimentallyCapturedImage(
    semantic_models.ExperimentallyCapturedImage,
    DocumentMixin,
):
    acquisition_process: List[UUID] = Field()
    representation: List[UUID] = Field()
    submission_dataset: UUID = Field()
    subject: Specimen = Field()
    # note Specimen is included in image document, but needs to be overriden to link to protocol & biosample via uuid.


class ImageAcquisition(
    semantic_models.ImageAcquisition,
    DocumentMixin,
    UserIdentifiedObject,
):
    pass


class SpecimenPrepartionProtocol(
    semantic_models.SpecimenPrepartionProtocol,
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
    image: List[UUID] = Field()
    file: List[UUID] = Field()
    annotation_file: List[UUID] = Field()
    submitted_in_study: UUID = Field()
    annotation_method: UUID = Field()


class AnnotationFileReference(
    semantic_models.AnnotationFileReference,
    DocumentMixin,
):
    source_image: List[UUID] = Field()
    submission_dataset: UUID = Field()
    creation_process: UUID = Field()


class DerivedImage(
    semantic_models.DerivedImage,
    DocumentMixin,
):
    source_image: List[UUID] = Field()
    submission_dataset: UUID = Field()
    creation_process: UUID = Field()
    representation: List[UUID] = Field()


class AnnotationMethod(
    semantic_models.AnnotationMethod,
    DocumentMixin,
    UserIdentifiedObject,
):
    source_dataset: List[Union[UUID, AnyUrl]]
