import json
import logging
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import click
import requests
from pydantic import BaseModel
from bia_integrator_core.integrator import load_and_annotate_study

from bia_integrator_tools.io import put_string_to_s3, get_s3_key_prefix, c2zsettings
from bia_integrator_tools.utils import get_ome_ngff_rep


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
    omero: Omero
    multiscales: List[MultiScaleImage]


def replace_first_channel_color(image):

    ngff_rep = get_ome_ngff_rep(image)

    zattrs_uri = f"{ngff_rep.uri}/.zattrs"

    r = requests.get(zattrs_uri)
    # print(r.content.decode())

    # zmeta = ZMeta.parse_raw(r.content)

    # print(zmeta)

    zobj = json.loads(r.content.decode())

    zobj["omero"]["channels"][0]["color"] = "FFFFFF"

    as_indented_str = json.dumps(zobj, indent=2)

    dst_key_as_path = Path(urlparse(zattrs_uri).path).relative_to(f"/{c2zsettings.bucket_name}")

    put_string_to_s3(as_indented_str, str(dst_key_as_path))


def write_back_zmeta(accession_id: str, image_id: str, zmeta: ZMeta):
    pass

def get_zmeta(accession_id, image_id):
    pass


@click.command()
@click.argument("accession_id")
@click.argument("image_id")
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    image = bia_study.images[image_id]

    ngff_rep = get_ome_ngff_rep(image)
    zattrs_uri = f"{ngff_rep.uri}/.zattrs"

    r = requests.get(zattrs_uri)
    zmeta = ZMeta.parse_raw(r.content)

    # Write a backup
    with open(f"{accession_id}.backup.zattrs", "w") as fh:
        fh.write(r.content.decode())

    # Make channels visible & set colours
    zmeta.omero.channels[3].active = True
    zmeta.omero.channels[3].color = "FFFF00"

    zmeta.omero.channels[4].active = True
    zmeta.omero.channels[4].color = "00FFFF"

    # Get key and write back to S3
    dst_key_as_path = Path(urlparse(zattrs_uri).path).relative_to(f"/{c2zsettings.bucket_name}")
    put_string_to_s3(zmeta.json(indent=2), str(dst_key_as_path))


if __name__ == "__main__":
    main()