
import logging
import pathlib
import tempfile
import subprocess
from zipfile import ZipFile

import click

from bia_integrator_core.config import Settings
from bia_integrator_core.interface import (
    api_models,
    persist_image_representation,
    get_filerefs
)
from bia_integrator_tools.io import (
    stage_fileref_and_get_fpath, upload_dirpath_as_zarr_image_rep
)
from bia_integrator_tools.utils import (
    get_image_rep_by_type,
    list_of_objects_to_dict,
)

logger = logging.getLogger(__file__)

def concatenate_files(input_list: list[str], output_path: str):
    """Concatenate files (binary assumed) in input_list to output_path"""

    command = f"cat {' '.join(input_list)} > {output_path}"
    logger.info(f"Concatenating files with command: {command}")
    retval = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert retval.returncode == 0, f"Error concatenating files: {retval.stderr.decode('utf-8')}"



def unzip_and_get_path_of_contents(zip_fpath, td):
    zf = ZipFile(zip_fpath)
    dirpath = pathlib.Path(td)
    logger.info(f"Unzipping to {dirpath}")
    zf.extractall(path=dirpath)

    # Assume unzipped contents contain a single top level .zarr dir
    # Otherwise check if zarr contents were zipped without top level .zarr dir
    dirpath_list = list(dirpath.glob("*"))
    if len(dirpath_list) == 1:
        src_dirpath = dirpath_list[0]
    elif (dirpath / ".zattrs").exists() or (dirpath / ".zgroup").exists():
        src_dirpath = dirpath
    else:
        raise (f"Unexpected zip contents structure: {dirpath_list}. Expected single top-level .zarr directory")

    return src_dirpath


@click.command()
@click.argument("accession_id")
@click.argument("image_uuid")
def main(accession_id, image_uuid):
    logging.basicConfig(level=logging.INFO)

    file_references = list_of_objects_to_dict(get_filerefs(accession_id))
    zipped_zarr_rep = get_image_rep_by_type(image_uuid, "zipped_zarr")
    # We may have split zips!
    zip_fpath_list = []
    for fileref_id in zipped_zarr_rep.attributes["fileref_ids"]:
        fileref = file_references[fileref_id]
        zip_fpath_list.append(str(stage_fileref_and_get_fpath(accession_id, fileref)))

    path_in_zarr = zipped_zarr_rep.attributes.get("path_in_zarr", "")

    if len(zip_fpath_list) == 1:
        zip_fpath = zip_fpath_list[0]
    else:
        zip_fpath = str(pathlib.Path(zip_fpath_list[0]).parent / f"{image_uuid}.zip")
        concatenate_files(input_list=zip_fpath_list, output_path=zip_fpath)

    # Use configurable cache location because /tmp on some codon nodes
    # run out of memory when unzipping large zarr archives    
    cache_dirpath = Settings().cache_root_dirpath
    with tempfile.TemporaryDirectory(dir=cache_dirpath) as td:
        src_dirpath = unzip_and_get_path_of_contents(zip_fpath, td)

        logger.info(f"Unzipped to {src_dirpath}")

        uri = upload_dirpath_as_zarr_image_rep(src_dirpath, accession_id, image_uuid)
        uri += path_in_zarr

    rep = api_models.BIAImageRepresentation(
        size=0,
        type="ome_ngff",
        uri=[uri,],
        dimensions=None,
        rendering=None,
        attributes={}
    )
    persist_image_representation(image_uuid, rep)


if __name__ == "__main__":
    main()
