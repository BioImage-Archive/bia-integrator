"""Copies an unconverted png or jpeg image to s3."""
import logging
import pathlib
import tempfile
import subprocess
from zipfile import ZipFile

import click

from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_image_representation
from bia_integrator_tools.io import (
    stage_fileref_and_get_fpath, copy_local_to_s3, get_s3_key_prefix
)
from bia_integrator_tools.utils import get_fileref_for_png_jpg

logger = logging.getLogger(__file__)


@click.command()
@click.argument("accession_id")
@click.argument("image_id")
def main(accession_id, image_id):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    image = bia_study.images[image_id]
    fileref_id = get_fileref_for_png_jpg(image,rep_type='fire_object')
    fileref = bia_study.file_references[fileref_id]

    im_fpath = stage_fileref_and_get_fpath(accession_id, fileref)
    ext = pathlib.PurePath(image.name).suffix
    dst_key = get_s3_key_prefix(accession_id,image_id) + ext
    uri = copy_local_to_s3(im_fpath, dst_key)

    rep = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=0,
        type="unconverted",
        uri=uri,
        dimensions=None,
        rendering=None,
        attributes={}
    )
    persist_image_representation(rep)


if __name__ == "__main__":
    main()