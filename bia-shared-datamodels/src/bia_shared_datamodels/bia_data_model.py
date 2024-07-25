from __future__ import annotations

from . import semantic_models
from . import exceptions
from pydantic import BaseModel, ConfigDict, Field, AnyUrl
from typing import List, Optional, Union
from uuid import UUID

from pydantic_core import Url

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
        Optional so we can accept objects without it set and set it on the server.
        Can't default_factory because that can't be generated in the api client."""
    )

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
    experimental_imaging_component: List[UUID] = Field()
    annotation_component: List[UUID] = Field()
    author: List[semantic_models.Contributor] = Field(min_length=1)
    description: str = Field()


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
    preparation_method: List[UUID] = Field(min_length=1)
    sample_of: List[UUID] = Field(min_length=1)


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
    annotation_method: List[UUID] = Field()


class AnnotationFileReference(
    semantic_models.AnnotationFileReference,
    DocumentMixin,
):
    source_image: List[UUID] = Field()
    submission_dataset: UUID = Field()
    creation_process: List[UUID] = Field()


class DerivedImage(
    semantic_models.DerivedImage,
    DocumentMixin,
):
    source_image: List[UUID] = Field()
    submission_dataset: UUID = Field()
    creation_process: List[UUID] = Field()
    representation: List[UUID] = Field()


class AnnotationMethod(
    semantic_models.AnnotationMethod,
    DocumentMixin,
    UserIdentifiedObject,
):
    source_dataset: List[Union[UUID, AnyUrl]]