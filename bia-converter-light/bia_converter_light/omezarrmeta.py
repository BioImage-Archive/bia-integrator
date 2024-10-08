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
    family: Optional[str] = None
    inverted: Optional[bool] = None


class Omero(BaseModel):
    rdefs: RDefs
    channels: List[Channel]


class CoordinateTransformation(BaseModel):
    scale: List[float]
    type: str


class DataSet(BaseModel):
    path: str
    coordinateTransformations: Optional[List[CoordinateTransformation]] = None


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
    axes: Optional[List[Axis]] = None
    version: str


class Column(BaseModel):
    name: str


class Row(BaseModel):
    name: str


class Well(BaseModel):
    columnIndex: int
    path: str
    rowIndex: int


class Plate(BaseModel):
    columns: List[Column]
    rows: List[Row]
    wells: List[Well]
    version: str


class ZMeta(BaseModel):
    omero: Optional[Omero] = None
    multiscales: Optional[List[MultiScaleImage]] = []
    plates: Optional[Plate] = None
