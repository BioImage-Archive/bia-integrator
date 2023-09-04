from enum import Enum
from pydantic import BaseModel, Field, BaseConfig, PrivateAttr, validator
from typing import Dict, List, Optional, Union, AnyStr
from pathlib import Path
from ome_types import OME, from_xml
from urllib.parse import urlparse, urlunparse
from bson import ObjectId, errors
from uuid import UUID
import requests

from src.api.exceptions import DocumentNotFound

class BIABaseModel(BaseModel):
    def json(self, ensure_ascii=False, **kwargs):
        """ensure_ascii defaults to False instead of True to handle the common case of non-ascii names"""

        return super().json(ensure_ascii=ensure_ascii, **kwargs)

class OID(str):
  @classmethod
  def __get_validators__(cls):
      yield cls.validate

  @classmethod
  def validate(cls, v):
      try:
          return ObjectId(str(v))
      except errors.InvalidId:
          raise ValueError("Not a valid ObjectId")

class ModelMetadata(BaseModel):
    type_name: str = Field()
    version: int = Field()

class DocumentMixin(BaseModel):
    # id optional only when creating documents, in all other cases it is required and gets manually verified
    # so it's OR(no id no model defined, both defined)
    id: Optional[OID] = Field(alias="_id")
    uuid: UUID = Field()
    # this is the document version, not the model version
    version: int = Field()

    # model is actually always set on objects, but in __init__ since that's where we are aware of child classes
    model: Optional[ModelMetadata] = Field(default=None)

    def __init__(self, apply_annotations = True, **data):
        if not hasattr(self.__class__.Config, 'model_version_latest'):
            raise ValueError(f"Class {self.__class__.__name__} missing 'model_version_latest' in its Config")
        model_metadata_expected = ModelMetadata(
            type_name=self.__class__.__name__,
            # @TODO: maybe eventually change model_version_latest to handle next-version migrations?
            version=self.__class__.Config.model_version_latest
        )

        if data.get('_id', None):
            # document comes from mongo, expect ModelMetadata to match
            model_metadata_existing = data.get('model', None)
            if model_metadata_existing:
                model_metadata_existing = ModelMetadata(**model_metadata_existing)

                if model_metadata_existing != model_metadata_expected:
                    raise DocumentNotFound(f"Document {str(data.get('_id'))} has model metadata {model_metadata_existing}, expected : {model_metadata_expected}")
            else:
                raise ValueError(f"Document missing model attribute")
        else:
            # document created now, will pe persisted later - add model
            if data.get("model", None):
                raise ValueError("Expecting models that were not persisted to not have a model either")
            data["model"] = model_metadata_expected
        
        # build the object before applying annotations so that model defaults get overwritten by annotations if necessary
        super().__init__(**data)

        if apply_annotations and hasattr(self, 'annotations'):
            document_attributes = set(self.__dict__.keys())

            for annotation in self.annotations:
                if annotation.key in ["model", "_id", "uuid"]:
                    raise Exception(f"Annotation {annotation} of object {self.uuid} overwrites a read-only property")

                if annotation.key in document_attributes:
                    self.__dict__[annotation.key] = annotation.value
                else:
                    self.attributes[annotation.key] = annotation.value

    def dict(self, *args, **kwargs):
        doc_dict = super().dict(*args, **kwargs)
        if 'id' in doc_dict:
            del doc_dict['id']

        return doc_dict

    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {
            #datetime: lambda dt: dt.isoformat(),
            ObjectId: lambda oid: str(oid)
        }

class Author(BIABaseModel):
    name: str

class AnnotationState(str, Enum):
    active = "active",
    deleted = "deleted"

class Annotation(BIABaseModel):
    author_email: str = Field()
    key: str = Field()
    value: str = Field()
    state: AnnotationState = Field()

class ImageAnnotation(Annotation):
    pass

class StudyAnnotation(Annotation):
    pass

class BIAStudy(BIABaseModel, DocumentMixin):
    title: str = Field()
    description: str = Field()
    authors: Optional[List[Author]] = Field(default=[])
    organism: str = Field()
    release_date: str = Field()
    accession_id: str = Field()
    
    imaging_type: List[str] = Field(default=[])
    attributes: Dict = Field(default={})
    annotations: List[StudyAnnotation] = Field(default=[])
    example_image_uri: str = Field(default="")
    example_image_annotation_uri: str = Field(default="")
    tags: List[str] = Field(default=[])

    file_references_count: int = Field(default=0)
    images_count: int = Field(default=0)

    class Config(BaseConfig):
        model_version_latest = 1

class FileReference(BIABaseModel, DocumentMixin):
    """A reference to an externally hosted file."""

    study_uuid: UUID = Field()
    name: str = Field()
    uri: str = Field()
    type: str = Field()
    size_bytes: int = Field()
    attributes: Dict = Field(default={})

    class Config(BaseConfig):
        model_version_latest = 1

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

class BIAOmeMetadata(dict):
    pass

class BIAImage(BIABaseModel, DocumentMixin):
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
    original_relpath: str = Field() # originally Path
    name: Optional[str] = Field(default=None)

    dimensions: Optional[str] = Field(default=None)
    representations: List[BIAImageRepresentation] = Field(default=[])
    attributes: Dict = Field(default={})
    annotations: List[ImageAnnotation] = Field(default=[])
    alias: Optional[BIAImageAlias] = Field(default=None)

    @property
    def ome_metadata(self) -> Optional[BIAOmeMetadata]:
        metadata = self.__dict__.get('ome_metadata', None)
        if metadata is None:
            ngff_rep = [rep for rep in self.representations if rep.type == "ome_ngff"]
            if not ngff_rep:
                return None
            else:
                # If the same image has multiple ngff representations, assume metadata is the same
                ngff_rep = ngff_rep.pop()
                parsed_url = urlparse(ngff_rep.uri)
                ome_metadata_path = Path(parsed_url.path).parent/"OME/METADATA.ome.xml"
                ome_metadata_uri = urlunparse((
                    parsed_url.scheme, parsed_url.netloc, str(ome_metadata_path),
                    None,
                    None,
                    None
                ))

                metadata = BIAImage._ome_xml_url_parse(ome_metadata_uri)
                self.__dict__['ome_metadata'] = metadata

        return metadata

    @classmethod
    def _ome_xml_url_parse(cls, ome_metadata_uri: AnyStr) -> Optional[OME]:    
        r = requests.get(ome_metadata_uri)
        assert r.status_code == 200, f"Error {r.status_code} fetching URI '{ome_metadata_uri}: {r.content}"

        ome_metadata = from_xml(r.content, parser='lxml', validate=False)

        return ome_metadata

    class Config(BaseConfig):
        model_version_latest = 1

class BIACollection(BIABaseModel, DocumentMixin):
    """A collection of studies with a coherent purpose. Studies can be in
    multiple collections."""
    name: str = Field()
    title: str = Field()
    subtitle: str = Field()
    description: Optional[str] = Field(default=None)
    study_uuids: List[str] = Field(default=[])

    class Config(BaseConfig):
        model_version_latest = 1

class User(BIABaseModel, DocumentMixin):
    email: Union[str, None] = None
    password: str

    class Config(BaseConfig):
        model_version_latest = 1
