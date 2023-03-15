import hashlib
import logging
from zipfile import ZipFile
from pathlib import Path
from urllib.parse import urlparse

import click
from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.interface import persist_image_representation
from bia_integrator_core.integrator import load_and_annotate_study

from bia_integrator_tools.conversion import run_zarr_conversion
from bia_integrator_tools.io import copy_uri_to_local, copy_local_zarr_to_s3


logger = logging.getLogger(__file__)


def rep_by_type(image, rep_type):
    for representation in image.representations:
        if representation.type == rep_type:
            return representation


@click.command()
@click.argument("accession_id")
@click.argument("image_id")
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    cache_dirpath = Path.home()/".cache"/"bia-converter"
    cache_dirpath.mkdir(exist_ok=True, parents=True)

    bia_study = load_and_annotate_study(accession_id)
    image = bia_study.images[image_id]

    zipfile_rep = rep_by_type(image, "zipfile")

    prefix = hashlib.md5(zipfile_rep.uri.encode()).hexdigest()
    suffix = Path(urlparse(zipfile_rep.uri).path).suffix
    dst_fname = prefix+suffix
    dst_fpath = cache_dirpath/dst_fname

    if not dst_fpath.exists():
        copy_uri_to_local(zipfile_rep.uri, dst_fpath)
        logger.info(f"Downloading zipfile to {dst_fpath}")
    else:
        logger.info(f"Zipfile exists at {dst_fpath}")

    zipfile_fpath = dst_fpath

    with ZipFile(zipfile_fpath) as zipfile:
        image_local_fpath = zipfile.extract(zipfile_rep.attributes["zip_filename"], cache_dirpath/accession_id)

    output_zarr_dirpath = cache_dirpath/accession_id/f"{image_id}.zarr"

    run_zarr_conversion(image_local_fpath, output_zarr_dirpath)
    zarr_image_uri = copy_local_zarr_to_s3(output_zarr_dirpath, accession_id, image_id)

    representation = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=0,
        type="ome_ngff",
        uri=zarr_image_uri,
        dimensions=None
    )

    persist_image_representation(representation)


if __name__ == "__main__":
    main()