import logging
from pathlib import Path

import click
import shutil
import requests


from bia_integrator_tools.io import copy_local_zarr_to_s3, stage_fileref_and_get_fpath
from bia_integrator_tools.conversion import run_zarr_conversion
from bia_integrator_core.interface import (
    api_models,
    persist_image_representation,
    get_filerefs,
)
from bia_integrator_tools.utils import (
    get_image_rep_by_type,
    list_of_objects_to_dict,
)

logger = logging.getLogger(__file__)


def copy_uri_to_local(src_uri: str, dst_fpath: Path):
    """Copy the object at the given source URI to the local path specified by dst_fpath."""

    logger.info(f"Fetching {src_uri} to {dst_fpath}")

    with requests.get(src_uri, stream=True) as r:
        with open(dst_fpath, "wb") as fh:
            shutil.copyfileobj(r.raw, fh)


@click.command()
@click.argument("accession_id")
@click.argument("image_uuid")
@click.option(
    "--save-to-file", is_flag=True, default=False, help="Save representation to file"
)
def main(accession_id, image_uuid, save_to_file):
    logging.basicConfig(level=logging.INFO)

    file_references = list_of_objects_to_dict(get_filerefs(accession_id))
    rep = get_image_rep_by_type(image_uuid, "fire_object")

    assert (
        len(rep.attributes["fileref_ids"]) == 1
    ), "This conversion script only works with single fileref image representations"

    fileref_id = rep.attributes["fileref_ids"][0]
    fileref = file_references[fileref_id]
    input_fpath = stage_fileref_and_get_fpath(accession_id, fileref)

    dst_dir_basepath = Path("tmp/c2z") / accession_id
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)

    zarr_fpath = dst_dir_basepath / f"{image_uuid}.zarr"
    if not zarr_fpath.exists():
        run_zarr_conversion(input_fpath, zarr_fpath)

    zarr_image_uri = copy_local_zarr_to_s3(zarr_fpath, accession_id, image_uuid)

    representation = api_models.BIAImageRepresentation(
        size=0,
        type="ome_ngff",
        uri=[
            zarr_image_uri,
        ],
        dimensions=None,
        rendering=None,
        attributes={},
    )

    if not save_to_file:
        persist_image_representation(image_uuid, representation)
    else:
        fname = f"{accession_id}-{image_uuid}.json"
        logger.info(f"Saving to {fname}")
        with open(fname, "w") as fh:
            fh.write(representation.json(indent=2))


if __name__ == "__main__":
    main()
