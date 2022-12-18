import pathlib
from typing import Dict, List, Optional, Set

from pydantic import BaseModel


class BIAImageRepresentation(BaseModel):
    accession_id: str
    image_id: str
    uri: str
    size: int
    type: Optional[str]
    dimensions: Optional[str]
    attributes: Optional[Dict]


class BIAFileRepresentation(BaseModel):
    accession_id: str
    file_id: str
    uri: str
    size: int


class BIAFile(BaseModel):
    id: str
    original_relpath: pathlib.Path
    original_size: int
    attributes: Dict = {}
    representations: List[BIAFileRepresentation] = []


class BIAImage(BaseModel):
    id: str
    original_relpath: pathlib.Path
    dimensions: Optional[str]
    representations: List[BIAImageRepresentation] = []
    attributes: Dict = {}


class Author(BaseModel):
    name: str


class BIAStudy(BaseModel):
    accession_id: str
    title: str
    description: str
    authors: Optional[List[Author]] = []
    organism: str
    release_date: str
    imaging_type: Optional[str]
    attributes: Dict = {}
    example_image_uri: str = ""

    images: Dict[str, BIAImage] = {}
    archive_files: Dict[str, BIAFile] = {}
    other_files: Dict[str, BIAFile] = {}

    tags: Set[str] = set()


class BIACollection(BaseModel):
    name: str
    title: str
    subtitle: str
    description: Optional[str]
    accession_ids: List[str]


class StudyTag(BaseModel):
    accession_id: str
    value: str


class StudyAnnotation(BaseModel):
    accession_id: str
    key: str
    value: str


class ImageAnnotation(BaseModel):
    accession_id: str
    image_id: str
    key: str
    value: str