from __future__ import annotations

from . import semantic_models, exceptions
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from enum import Enum


class ModelMetadata(BaseModel):
    type_name: str = Field()
    version: int = Field()


class DocumentMixin(BaseModel):
    uuid: UUID = Field(
        description="""Unique ID (across the BIA database) used to refer to and identify a document."""
    )

    version: int = Field(
        description="""Document version. This can't be optional to make sure we never persist objects without it"""
    )
    model: Optional[ModelMetadata] = Field(
        description="""Model type and version. Used to map arbitrary objects to a known (possibly previously-used) type.
        Optional because for some usecases (e.g. api) we want to accept objects without it because we have the info we need to set it."""
    )

    # Throw error if you try to validate/create model from a dictionary with keys that aren't a field in the model
    model_config = ConfigDict(extra="forbid")

    def __init__(self, *args, **data):
        model_version_spec = self.model_config.get("model_version_latest")
        if model_version_spec is None:
            raise exceptions.ModelDefinitionInvalid(
                f"Class {self.__class__.__name__} missing 'model_version_latest' in its model_config"
            )

        model_metadata_expected = ModelMetadata(
            type_name=self.__class__.__name__,
            version=model_version_spec,
        )
        model_metadata_existing = data.get("model", None)
        if model_metadata_existing:
            if model_metadata_existing != model_metadata_expected:
                raise exceptions.UnexpectedDocumentType(
                    f"Document {str(data.get('uuid'))} has model metadata {model_metadata_existing}, expected : {model_metadata_expected}"
                )
        else:
            data["model"] = model_metadata_expected.model_dump()

        super().__init__(*args, **data)


class UserIdentifiedObject(BaseModel):
    title_id: str = Field(
        description="""User provided title, which is unqiue within a submission, used to identify a part of a submission."""
    )


class Study(
    semantic_models.Study,
    DocumentMixin,
):
    author: List[semantic_models.Contributor] = Field(min_length=1)

    model_config = ConfigDict(model_version_latest=1)


class FileReference(
    semantic_models.FileReference,
    DocumentMixin,
):
    submission_dataset_uuid: UUID = Field()

    model_config = ConfigDict(model_version_latest=1)


class ImageRepresentation(
    semantic_models.ImageRepresentation,
    DocumentMixin,
):
    # We may want to store the FileReference -> Image(Represenation) rather than in the original_file_reference_uuid
    original_file_reference_uuid: Optional[List[UUID]] = Field()
    representation_of_uuid: UUID = Field()

    model_config = ConfigDict(model_version_latest=1)


class ExperimentalImagingDataset(
    semantic_models.ExperimentalImagingDataset,
    DocumentMixin,
    UserIdentifiedObject,
):
    submitted_in_study_uuid: UUID = Field()

    model_config = ConfigDict(model_version_latest=1)


class Specimen(semantic_models.Specimen, DocumentMixin):
    imaging_preparation_protocol_uuid: List[UUID] = Field(min_length=1)
    sample_of_uuid: List[UUID] = Field(min_length=1)
    growth_protocol_uuid: List[UUID] = Field()

    model_config = ConfigDict(model_version_latest=1)


class ExperimentallyCapturedImage(
    semantic_models.ExperimentallyCapturedImage,
    DocumentMixin,
):
    acquisition_process_uuid: List[UUID] = Field()
    submission_dataset_uuid: UUID = Field()
    subject_uuid: UUID = Field()

    model_config = ConfigDict(model_version_latest=1)


class ImageAcquisition(
    semantic_models.ImageAcquisition,
    DocumentMixin,
    UserIdentifiedObject,
):
    model_config = ConfigDict(model_version_latest=1)


class SpecimenImagingPrepartionProtocol(
    semantic_models.SpecimenImagingPrepartionProtocol,
    DocumentMixin,
    UserIdentifiedObject,
):
    model_config = ConfigDict(model_version_latest=1)


class SpecimenGrowthProtocol(
    semantic_models.SpecimenGrowthProtocol,
    DocumentMixin,
    UserIdentifiedObject,
):
    model_config = ConfigDict(model_version_latest=1)


class BioSample(
    semantic_models.BioSample,
    DocumentMixin,
    UserIdentifiedObject,
):
    model_config = ConfigDict(model_version_latest=1)


class ImageAnnotationDataset(
    semantic_models.ImageAnnotationDataset,
    DocumentMixin,
    UserIdentifiedObject,
):
    submitted_in_study_uuid: UUID = Field()

    model_config = ConfigDict(model_version_latest=1)


class AnnotationFileReference(
    semantic_models.AnnotationFileReference,
    DocumentMixin,
):
    submission_dataset_uuid: UUID = Field()
    source_image_uuid: List[UUID] = Field()
    creation_process_uuid: List[UUID] = Field()

    model_config = ConfigDict(model_version_latest=1)


class DerivedImage(
    semantic_models.DerivedImage,
    DocumentMixin,
):
    source_image_uuid: List[UUID] = Field()
    submission_dataset_uuid: UUID = Field()
    creation_process_uuid: List[UUID] = Field()

    model_config = ConfigDict(model_version_latest=1)


class AnnotationMethod(
    semantic_models.AnnotationMethod,
    DocumentMixin,
    UserIdentifiedObject,
):
    model_config = ConfigDict(model_version_latest=1)
