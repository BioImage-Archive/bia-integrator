from __future__ import annotations

from . import semantic_models, exceptions
from pydantic import BaseModel, Field, ConfigDict
from pydantic.fields import FieldInfo
from typing import List, Optional, Any, Dict
from uuid import UUID
from typing_extensions import Annotated, Union


class ObjectReference:
    """
    Instance context for "what does this link to"
    """

    link_dest_type: Any = BaseModel
    workaround_union_reference_types: Optional[List]

    def __init__(
        self, link_dest_type, workaround_union_reference_types: Optional[List] = None
    ):
        self.link_dest_type = link_dest_type
        self.workaround_union_reference_types = workaround_union_reference_types


class ModelMetadata(BaseModel):
    type_name: str = Field()
    version: int = Field()


class DocumentMixin(BaseModel):
    uuid: UUID = Field(
        description="""Unique ID (across the BIA database) used to refer to and identify a document."""
    )

    # !!!!
    # EXTREMELY important that this field is validated
    # please check no downstream breakage (especially api) before changing
    version: int = Field(
        description="""Document version. This can't be optional to make sure we never persist objects without it""",
        ge=0,
    )
    model: Optional[ModelMetadata] = Field(
        description="""Model type and version. Used to map arbitrary objects to a known (possibly previously-used) type.
        Optional because for some usecases (e.g. api) we want to accept objects without it because we have the info we need to set it.""",
        default=None,
    )

    def __init__(self, *args, **data):
        model_metadata_expected = self.get_model_metadata()
        model_metadata_existing = data.get("model", None)
        if model_metadata_existing:
            model_metadata_existing = ModelMetadata(**model_metadata_existing)
            if model_metadata_existing != model_metadata_expected:
                raise exceptions.UnexpectedDocumentType(
                    f"Document {str(data.get('uuid'))} has model metadata {model_metadata_existing}, expected : {model_metadata_expected}"
                )
        else:
            data["model"] = model_metadata_expected.model_dump()

        super().__init__(*args, **data)

    @classmethod
    def get_model_metadata(cls) -> ModelMetadata:
        model_version_spec = cls.model_config.get("model_version_latest")
        if model_version_spec is None:
            raise exceptions.ModelDefinitionInvalid(
                f"Class {cls.__name__} missing 'model_version_latest' in its model_config"
            )

        return ModelMetadata(
            type_name=cls.__name__,
            version=model_version_spec,
        )

    @classmethod
    def get_object_reference_fields(cls) -> Dict[str, ObjectReference]:
        """
        @return mapping of attribute_name: referenced_object_type
        """

        fields_filtered = {}
        for field_name, field_info in cls.model_fields.items():
            maybe_reference = next(
                (m for m in field_info.metadata if isinstance(m, ObjectReference)), None
            )

            if maybe_reference:
                fields_filtered[field_name] = maybe_reference

        return fields_filtered

    @classmethod
    def field_is_list(cls, field_name: str):
        """
        Helper to avoid leaking type introspection into user code

        @TODO: ! Ignored attribute missing exception
        """
        field_annotation_type = cls.model_fields[field_name].annotation
        if not getattr(field_annotation_type, "__origin__", None):
            # Not a generic, not even checking
            return False

        # Unpack Optional[*]
        if (
            field_annotation_type.__origin__ is Union
            and type(None) in field_annotation_type.__args__
        ):
            field_annotation_type = field_annotation_type.__args__[0]

            # check again in case it's Optional[SomeNonGenericType]
            if not getattr(field_annotation_type, "__origin__", None):
                # Not a generic, not even checking
                return False

            # it was Optional[SomeGenericType]

        return field_annotation_type.__origin__ is list

    @classmethod
    def fields_by_type(cls, field_type: Any) -> Dict[str, FieldInfo]:
        """
        @param field_type is the _actual class_ (not class name as a string) to search for
            typed as any because it can be a descendent of DocumentMixin or UUID
        """
        fields_filtered = {}

        for field_name, field_info in cls.model_fields.items():
            # conditions split for clarity
            field_type_exact = field_info.annotation is field_type
            field_type_container_list = (
                hasattr(field_info.annotation, "__origin__")
                and field_info.annotation.__origin__ is list
                and field_info.annotation.__args__[0] is field_type
            )
            if field_type_exact or field_type_container_list:
                fields_filtered[field_name] = field_info

        return fields_filtered


class UserIdentifiedObject(BaseModel):
    title_id: str = Field(
        description="""User provided title, which is unqiue within a submission, used to identify a part of a submission."""
    )


class Study(
    semantic_models.Study,
    DocumentMixin,
):
    author: List[semantic_models.Contributor] = Field(min_length=1)

    model_config = ConfigDict(model_version_latest=2)


class FileReference(
    semantic_models.FileReference,
    DocumentMixin,
):
    submission_dataset_uuid: Annotated[
        UUID,
        ObjectReference(
            None,
            workaround_union_reference_types=[
                ImageAnnotationDataset,
                ExperimentalImagingDataset,
            ],
        ),
    ] = Field()

    model_config = ConfigDict(model_version_latest=2)


class ImageRepresentation(
    semantic_models.ImageRepresentation,
    DocumentMixin,
):
    # We may want to store the FileReference -> Image(Represenation) rather than in the original_file_reference_uuid
    original_file_reference_uuid: Annotated[
        Optional[List[UUID]], ObjectReference(FileReference)
    ] = Field(default_factory=lambda: [])
    representation_of_uuid: Annotated[
        UUID,
        ObjectReference(
            None,
            workaround_union_reference_types=[
                DerivedImage,
                ExperimentallyCapturedImage,
            ],
        ),
    ] = Field()

    model_config = ConfigDict(model_version_latest=2)


class ExperimentalImagingDataset(
    semantic_models.ExperimentalImagingDataset,
    DocumentMixin,
    UserIdentifiedObject,
):
    submitted_in_study_uuid: Annotated[UUID, ObjectReference(Study)] = Field()

    model_config = ConfigDict(model_version_latest=2)


class Specimen(semantic_models.Specimen, DocumentMixin):
    imaging_preparation_protocol_uuid: Annotated[
        List[UUID], ObjectReference(SpecimenImagingPreparationProtocol)
    ] = Field(min_length=1)
    sample_of_uuid: Annotated[List[UUID], ObjectReference(BioSample)] = Field(
        min_length=1
    )
    growth_protocol_uuid: Annotated[
        List[UUID], ObjectReference(SpecimenGrowthProtocol)
    ] = Field()

    model_config = ConfigDict(model_version_latest=1)


class ExperimentallyCapturedImage(
    semantic_models.ExperimentallyCapturedImage,
    DocumentMixin,
):
    acquisition_process_uuid: Annotated[
        List[UUID], ObjectReference(ImageAcquisition)
    ] = Field()
    submission_dataset_uuid: Annotated[
        UUID, ObjectReference(ExperimentalImagingDataset)
    ] = Field()
    subject_uuid: Annotated[UUID, ObjectReference(Specimen)] = Field()

    model_config = ConfigDict(model_version_latest=2)


class ImageAcquisition(
    semantic_models.ImageAcquisition,
    DocumentMixin,
    UserIdentifiedObject,
):
    model_config = ConfigDict(model_version_latest=1)


class SpecimenImagingPreparationProtocol(
    semantic_models.SpecimenImagingPreparationProtocol,
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
    submitted_in_study_uuid: Annotated[UUID, ObjectReference(Study)] = Field()

    model_config = ConfigDict(model_version_latest=2)


class AnnotationFileReference(
    semantic_models.AnnotationFileReference,
    DocumentMixin,
):
    submission_dataset_uuid: Annotated[
        UUID,
        ObjectReference(
            None,
            workaround_union_reference_types=[
                ImageAnnotationDataset,
                ExperimentalImagingDataset,
            ],
        ),
    ] = Field()
    source_image_uuid: Annotated[
        List[UUID],
        ObjectReference(
            None,
            workaround_union_reference_types=[
                DerivedImage,
                ExperimentallyCapturedImage,
            ],
        ),
    ] = Field()
    creation_process_uuid: Annotated[List[UUID], ObjectReference(AnnotationMethod)] = (
        Field()
    )

    model_config = ConfigDict(model_version_latest=2)


class DerivedImage(
    semantic_models.DerivedImage,
    DocumentMixin,
):
    source_image_uuid: Annotated[
        List[UUID],
        ObjectReference(
            None,
            workaround_union_reference_types=[
                DerivedImage,
                ExperimentallyCapturedImage,
            ],
        ),
    ] = Field()
    submission_dataset_uuid: Annotated[
        UUID, ObjectReference(ImageAnnotationDataset)
    ] = Field()
    creation_process_uuid: Annotated[List[UUID], ObjectReference(AnnotationMethod)] = (
        Field()
    )

    model_config = ConfigDict(model_version_latest=2)


class AnnotationMethod(
    semantic_models.AnnotationMethod,
    DocumentMixin,
    UserIdentifiedObject,
):
    model_config = ConfigDict(model_version_latest=2)


Specimen.model_rebuild()
ExperimentallyCapturedImage.model_rebuild()
