from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from pydantic.generics import GenericModel
from typing import Dict, List, Optional, TypeVar, Generic
from uuid import UUID

from pydantic_core import Url

from src.api.exceptions import UnexpectedDocumentType, InvalidRequestException


def url2str(self, val: Url) -> str:
    return str(val)


class BIABaseModel(BaseModel):
    def json(self, ensure_ascii=False, **kwargs):
        """ensure_ascii defaults to False instead of True to handle the common case of non-ascii names"""

        return super().model_dump_json(ensure_ascii=ensure_ascii, **kwargs)


class ModelMetadata(BaseModel):
    type_name: str = Field()
    version: int = Field()


class DocumentMixin(BaseModel):
    # id optional only when creating documents, in all other cases it is required and gets manually verified
    # so it's OR(no id no model defined, both defined)
    uuid: UUID = Field()
    # this is the document version, not the model version
    version: int = Field()

    # model is actually always set on objects, but in __init__ since that's where we are aware of child classes
    model: Optional[ModelMetadata] = Field(default=None)
    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    def __init__(self, *args, **data):
        if self.model_config.get("model_version_latest") is None:
            raise ValueError(
                f"Class {self.__class__.__name__} missing 'model_version_latest' in its model_config"
            )
        model_metadata_expected = ModelMetadata(
            type_name=self.__class__.__name__,
            # @TODO: maybe eventually change model_version_latest to handle next-version migrations?
            version=self.model_config["model_version_latest"],
        )

        if data.get("_id", None):
            # document comes from mongo, expect ModelMetadata to match
            model_metadata_existing = data.get("model", None)
            if model_metadata_existing:
                model_metadata_existing = ModelMetadata(**model_metadata_existing)

                if model_metadata_existing != model_metadata_expected:
                    raise UnexpectedDocumentType(
                        f"Document {str(data.get('uuid'))} has model metadata {model_metadata_existing}, expected : {model_metadata_expected}"
                    )
            else:
                raise ValueError(f"Document missing model attribute")
        else:
            # document created now, will pe persisted later - add model
            if data.get("model", None) is None:
                data["model"] = model_metadata_expected

        data.pop("_id", None)
        super().__init__(*args, **data)


class JSONLDMixin(BaseModel):
    context: Url = Field(alias="@context", default="")

    # custom field serializer for Urls to provide strings for mongoDB
    @field_serializer("context")
    def url2str(self, val) -> str:
        return str(val)


class AnnotationState(str, Enum):
    active = "active"
    deleted = "deleted"


class Annotation(BIABaseModel):
    # @TODO:
    # pattern=".*@ebi\.ac\.uk"
    # openapi only supports perl-style regexes, but Pydantic/FastAPI doesn't translate
    author_email: str = Field()
    key: str = Field()
    value: str = Field()
    state: AnnotationState = Field()


class ImageAnnotation(Annotation):
    pass


class StudyAnnotation(Annotation):
    pass


class FileReferenceAnnotation(Annotation):
    pass


class CollectionAnnotation(Annotation):
    pass


class ImageAcquisitionAnnotation(Annotation):
    pass


class SpecimenAnnotation(Annotation):
    pass


class BiosampleAnnotation(Annotation):
    pass


TAnnotation = TypeVar(
    "TAnnotation",
    Annotation,
    StudyAnnotation,
    ImageAnnotation,
    FileReferenceAnnotation,
    CollectionAnnotation,
)


class AnnotatedMixin(GenericModel, Generic[TAnnotation]):
    attributes: Dict = Field(
        default={},
        description="""
        When annotations are applied, the ones that have a key different than an object attribute (so they don't overwrite it) get saved here.
    """,
    )
    annotations_applied: bool = Field(
        False,
        description="""
        This acts as a dirty flag, with the purpose of telling apart objects that had some fields overwritten by applying annotations (so should be rejected when writing), and those that didn't.
    """,
    )
    annotations: List[TAnnotation] = Field(default=[])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Any instance of an Annotateable object getting created is assumed to from a client, not the db
        if self.annotations_applied:
            raise InvalidRequestException(
                f"Trying to load object after annotations were applied! This is not allowed, to avoid overwriting object fields. Object: {self.model_dump()}"
            )


class Author(BIABaseModel):
    name: str


class BIAStudy(
    BIABaseModel, DocumentMixin, JSONLDMixin, AnnotatedMixin[StudyAnnotation]
):
    title: str = Field()
    description: str = Field()
    authors: Optional[List[Author]] = Field(default=[])
    organism: str = Field()
    release_date: str = Field()
    accession_id: str = Field()

    imaging_type: Optional[str] = Field(default=None)
    example_image_uri: str = Field(default="")
    example_image_annotation_uri: str = Field(default="")
    tags: List[str] = Field(default=[])

    file_references_count: int = Field(default=0)
    images_count: int = Field(default=0)

    context: Url = Field(
        alias="@context",
        default="https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/StudyContext.jsonld",
    )

    model_config = ConfigDict(model_version_latest=1)


class FileReference(
    BIABaseModel, DocumentMixin, JSONLDMixin, AnnotatedMixin[FileReferenceAnnotation]
):
    """A reference to an externally hosted file."""

    study_uuid: UUID = Field()
    name: str = Field()
    uri: str = Field()
    type: str = Field()
    size_in_bytes: int = Field()

    context: Url = Field(
        alias="@context",
        default="https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/FileReferenceContext.jsonld",
    )

    model_config = ConfigDict(model_version_latest=1)


class ChannelRendering(BIABaseModel):
    channel_label: Optional[str]
    colormap_start: List[float]
    colormap_end: List[float]
    scale_factor: float = 1.0


class RenderingInfo(BIABaseModel):
    channel_renders: List[ChannelRendering] = Field(default=[])
    default_z: Optional[int] = Field(default=None)
    default_t: Optional[int] = Field(default=None)


class BIAImageAlias(BIABaseModel):
    """An alias for an image - a more convenient way to refer to the image than
    the full accession ID / UUID pair"""

    name: str = Field()


class BIAImageRepresentation(BIABaseModel):
    """A particular representation of a BIAImage. Examples:

    * A single HTTP accessible file.
    * Multiple HTTP accessible files, representing different channels, planes and time points.
    * An S3 accessible OME-Zarr.
    * A thumbnail."""

    size: int = Field()
    uri: List[str] = Field(default=[])
    type: Optional[str] = Field(default=None)
    dimensions: Optional[str] = Field(default=None)
    attributes: Dict = Field(default={})
    rendering: Optional[RenderingInfo] = Field(default=None)


class Biosample(
    BIABaseModel, DocumentMixin, AnnotatedMixin[BiosampleAnnotation], JSONLDMixin
):
    title: str = (
        Field()
    )  # is this a ST-only concern, or does it make sense for it to be in the models?
    organism_scientific_name: str = Field()
    organism_common_name: str = Field()
    organism_ncbi_taxon: str = Field()
    description: str = Field()
    biological_entity: str = Field()
    experimental_variables: List[str] = Field(default=[])
    extrinsic_variables: List[str] = Field(
        description="External treatment (e.g. reagent).", default=[]
    )
    intrinsic_variables: List[str] = Field(
        description="Intrinsic (e.g. genetic) alteration.", default=[]
    )
    context: Url = Field(
        alias="@context",
        default="https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/SpecimenContext.jsonld",
    )

    model_config = ConfigDict(model_version_latest=1)


class Specimen(
    BIABaseModel, DocumentMixin, AnnotatedMixin[SpecimenAnnotation], JSONLDMixin
):
    biosample_uuid: UUID = Field()

    title: str = (
        Field()
    )  # is this a ST-only concern, or does it make sense for it to be in the models?
    sample_preparation_protocol: str = Field()
    growth_protocol: str = Field()
    context: Url = Field(
        alias="@context",
        default="https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/SpecimenContext.jsonld",
    )

    model_config = ConfigDict(model_version_latest=1)


class ImageAcquisition(
    BIABaseModel, DocumentMixin, AnnotatedMixin[ImageAcquisitionAnnotation], JSONLDMixin
):
    specimen_uuid: UUID = Field()

    title: str = (
        Field()
    )  # is this a ST-only concern, or does it make sense for it to be in the models?
    imaging_instrument: str = Field(
        description="Textual description of the instrument used to capture the images."
    )
    image_acquisition_parameters: str = Field(
        description="How the images were acquired, including instrument settings/parameters."
    )
    imaging_method: str = (
        Field()
    )  # make this an Enum / restrict some other way? Distinguishing between "somewhat close to a controlled vocabulary" vs "completely free text" might be useful
    context: Url = Field(
        alias="@context",
        default="https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/ImageAcquisitionContext.jsonld",
    )

    model_config = ConfigDict(model_version_latest=1)


class BIAImage(
    BIABaseModel, DocumentMixin, JSONLDMixin, AnnotatedMixin[ImageAnnotation]
):
    """This class represents the abstract concept of an image. Images are
    generated by acquisition by instruments.

    Examples:

    * A single plane bright-field image of a bacterium.
    * A confocal fluorescence image of cells, with two channels.
    * A volume EM stack of a cell.

    Images are distinct from their representation as files, since the same
    image can be represented in different file formats and in some cases
    different file structures.
    """

    study_uuid: UUID = Field()
    original_relpath: str = Field()  # originally Path
    name: Optional[str] = Field(default=None)

    dimensions: Optional[str] = Field(default=None)
    representations: List[BIAImageRepresentation] = Field(default=[])
    alias: Optional[BIAImageAlias] = Field(default=None)
    image_acquisitions_uuid: List[UUID] = Field(
        description="Context in which the image was acquired.",
        default=[],
    )
    context: Url = Field(
        alias="@context",
        default="https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/ImageContext.jsonld",
    )

    model_config = ConfigDict(model_version_latest=2)


class BIACollection(
    BIABaseModel,
    DocumentMixin,
    JSONLDMixin,
    AnnotatedMixin[CollectionAnnotation],
):
    """A collection of studies with a coherent purpose. Studies can be in
    multiple collections."""

    name: str = Field()
    title: str = Field()
    subtitle: str = Field()
    description: Optional[str] = Field(default=None)
    study_uuids: List[str] = Field(default=[])
    context: Url = Field(
        alias="@context",
        default="https://raw.githubusercontent.com/BioImage-Archive/bia-integrator/main/api/src/models/jsonld/1.0/CollectionContext.jsonld",
    )

    model_config = ConfigDict(model_version_latest=1)


class User(BIABaseModel, DocumentMixin):
    email: str = Field()
    password: str = Field()

    model_config = ConfigDict(model_version_latest=1)


class BIAImageOmeMetadata(BIABaseModel, DocumentMixin):
    bia_image_uuid: UUID = Field()
    # just a dict to avoid cluttering openapi models in client/generated docs
    ome_metadata: dict = Field(
        description="The OME metadata as a json-compatible object. Can be used as a dictionary or directly parsed with the ome-types module."
    )

    model_config = ConfigDict(model_version_latest=1)
