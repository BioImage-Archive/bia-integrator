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
    family: str | None = None
    inverted: bool | None = None


class Omero(BaseModel):
    rdefs: RDefs
    channels: List[Channel]


class CoordinateTransformation(BaseModel):
    scale: List[float]
    type: str


class DataSet(BaseModel):
    path: str
    coordinateTransformations: Optional[List[CoordinateTransformation]]


class MSMetadata(BaseModel):
    method: str
    version: str


class Axis(BaseModel):
    name: str
    type: str
    unit: Optional[str] = None


class MultiScaleImage(BaseModel):
    datasets: List[DataSet]
    metadata: Optional[MSMetadata] = None
    name: Optional[str] = None
    axes: Optional[List[Axis]] = None
    version: Optional[str] = None


class ZMeta(BaseModel):
    omero: Optional[Omero] = None
    multiscales: List[MultiScaleImage]
