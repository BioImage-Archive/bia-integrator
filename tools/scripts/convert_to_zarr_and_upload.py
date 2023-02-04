import json
import logging
from pathlib import Path

import click
import shutil
import requests
from pydantic import BaseSettings


from bia_integrator_tools.io import copy_local_zarr_to_s3
from bia_integrator_tools.conversion import run_zarr_conversion
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.interface import persist_image_representation


logger = logging.getLogger(__file__)


def copy_uri_to_local(src_uri: str, dst_fpath: Path):
    """Copy the object at the given source URI to the local path specified by dst_fpath."""

    logger.info(f"Fetching {src_uri} to {dst_fpath}")

    with requests.get(src_uri, stream=True) as r:
        with open(dst_fpath, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)


@click.command()
@click.argument("accession_id")
@click.argument("image_id")
@click.option("--save-to-file", is_flag=True, default=False, help="Save representation to file")
def main(accession_id, image_id, save_to_file):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    image = bia_study.images[image_id]

    dst_dir_basepath = Path("tmp/c2z")/accession_id
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)

    image_suffix = image.original_relpath.suffix
    dst_fpath = dst_dir_basepath/f"{image_id}{image_suffix}"

    # FIXME - this should check for the correct representation type, not assume it's the first one
    src_uri = image.representations[0].uri
    if not dst_fpath.exists():
        copy_uri_to_local(src_uri, dst_fpath)

    zarr_fpath = dst_dir_basepath/f"{image_id}.zarr"
    if not zarr_fpath.exists():
        run_zarr_conversion(dst_fpath, zarr_fpath)

    zarr_image_uri = copy_local_zarr_to_s3(zarr_fpath, accession_id, image_id)

    representation = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=0,
        type="ome_ngff",
        uri=zarr_image_uri,
        dimensions=None,
        rendering=None,
        attributes={}
    )

    if not save_to_file:
        persist_image_representation(representation)
    else:
        fname = f"{accession_id}-{image_id}.json"
        logging.info(f"Saving to {fname}")
        with open(fname, "w") as fh:
            fh.write(representation.json(indent=2))
        



if __name__ == "__main__":
    main()