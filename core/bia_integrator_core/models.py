import pathlib
from typing import Dict, List, Optional

from pydantic import BaseModel


class BIAImageRepresentation(BaseModel):
    accession_id: str
    image_id: str
    uri: str
    size: int
    type: Optional[str]
    dimensions: Optional[str]
        

class BIAImage(BaseModel):
    id: str
    original_relpath: pathlib.Path
    dimensions: Optional[str]
    representations: List[BIAImageRepresentation] = []
    attributes: Dict = {}


class BIAStudy(BaseModel):
    accession_id: str
    title: str
    description: str
    organism: str
    release_date: str
    imaging_type: Optional[str]
    example_image_uri: str = ""

    images: Dict[str, BIAImage] = {}


class BIACollection(BaseModel):
    name: str
    title: str
    subtitle: str
    description: Optional[str]
    accession_ids: List[str]


class StudyAnnotation(BaseModel):
    accession_id: str
    key: str
    value: str

class ImageAnnotation(BaseModel):
    accession_id: str
    image_id: str
    key: str
    value: str