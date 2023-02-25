import pathlib
from typing import Dict, List, Optional, Set

from pydantic import BaseModel

class BIABaseModel(BaseModel):
    def json(self, ensure_ascii=False, **kwargs):
        """ensure_ascii defaults to False instead of True to handle the common case of non-ascii names"""

        return super().json(ensure_ascii=ensure_ascii, **kwargs)

class ChannelRendering(BIABaseModel):
    colormap_start: List[float]
    colormap_end: List[float]
    scale_factor: float = 1.0


class RenderingInfo(BIABaseModel):
    channel_renders: List[ChannelRendering]
    default_z: Optional[int]
    default_t: Optional[int]


class BIAImageRepresentation(BIABaseModel):
    accession_id: str
    image_id: str
    uri: str
    size: int
    type: Optional[str]
    dimensions: Optional[str]
    attributes: Optional[Dict]
    rendering: Optional[RenderingInfo]


class BIAFileRepresentation(BIABaseModel):
    accession_id: str
    file_id: str
    uri: str
    size: int


class BIAFile(BIABaseModel):
    id: str
    original_relpath: pathlib.Path
    original_size: int
    attributes: Dict = {}
    representations: List[BIAFileRepresentation] = []


class FileReference(BIABaseModel):
    """A reference to an externally hosted file."""

    id: str # A unique identifier for the file reference
    name: str # A short descriptive name
    uri: str # URI of the file
    size_in_bytes: Optional[int] # Size of the file
    attributes: Dict = {}


class BIAImage(BIABaseModel):
    accession_id: str
    id: str
    # TODO - rationalise these (name should probably replace original_relpath)
    name: Optional[str]
    original_relpath: pathlib.Path

    dimensions: Optional[str]
    representations: List[BIAImageRepresentation] = []
    attributes: Dict = {}


class Author(BIABaseModel):
    name: str


class BIAStudy(BIABaseModel):
    accession_id: str
    title: str
    description: str
    authors: Optional[List[Author]] = []
    organism: str
    release_date: str
    
    # FIXME - this should be a list
    imaging_type: Optional[str]
    attributes: Dict = {}
    example_image_uri: str = ""

    file_references: Dict[str, FileReference] = {}

    images: Dict[str, BIAImage] = {}
    archive_files: Dict[str, BIAFile] = {}
    other_files: Dict[str, BIAFile] = {}

    tags: Set[str] = set()


class BIACollection(BIABaseModel):
    name: str
    title: str
    subtitle: str
    description: Optional[str]
    accession_ids: List[str]


class StudyTag(BIABaseModel):
    accession_id: str
    value: str


class StudyAnnotation(BIABaseModel):
    accession_id: str
    key: str
    value: str


class ImageAnnotation(BIABaseModel):
    accession_id: str
    image_id: str
    key: str
    value: str