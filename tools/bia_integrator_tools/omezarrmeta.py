from typing import List, Optional

from pydantic import BaseModel


class RDefs(BaseModel):
    defaultT: int
    model: str
    defaultZ: int

class Window(BaseModel):
    min: float
    max: float
    start: float
    end: float

class Channel(BaseModel):
    color: str
    coefficient: int
    active: bool
    label: str
    window: Window
    family: str
    inverted: bool

class Omero(BaseModel):
    rdefs: RDefs
    channels: List[Channel]

class CoordinateTransformation(BaseModel):
    scale: List[float]
    type: str

class DataSet(BaseModel):
    path: str
    coordinateTransformations: List[CoordinateTransformation]

class MSMetadata(BaseModel):
    method: str
    version: str

class Axis(BaseModel):
    name: str
    type: str
    unit: Optional[str]

class MultiScaleImage(BaseModel):
    datasets: List[DataSet]
    metadata: MSMetadata
    axes: List[Axis]
    version: str

class ZMeta(BaseModel):
    omero: Optional[Omero]
    multiscales: List[MultiScaleImage]
