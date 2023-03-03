import logging
import pathlib
import tempfile
import subprocess
from zipfile import ZipFile

import click

from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_image_representation
from bia_integrator_tools.io import stage_fileref_and_get_fpath, c2zsettings
from bia_integrator_tools.utils import get_image_rep_by_type

logger = logging.getLogger(__file__)


def unzip_and_get_path_of_contents(zip_fpath, td):
    zf = ZipFile(zip_fpath)
    dirpath = pathlib.Path(td)
    logger.info(f"Unzipping to {dirpath}")
    zf.extractall(path=dirpath)

    dirpath_list = list(dirpath.glob("*"))
    assert len(dirpath_list) == 1
    src_dirpath = dirpath_list[0]

    return src_dirpath


def upload_dirpath_as_zarr_image_rep(src_dirpath, accession_id, image_id):

    dst_prefix = f"{c2zsettings.bucket_name}/{accession_id}/{image_id}/{image_id}.zarr"
    logger.info(f"Uploading with prefix {dst_prefix}")
    cmd = f"aws --region us-east-1 --endpoint-url {c2zsettings.endpoint_url} s3 sync {src_dirpath}/ s3://{dst_prefix} --acl public-read"
    subprocess.run(cmd, shell=True)

    uri = f"{c2zsettings.endpoint_url}/{c2zsettings.bucket_name}/{accession_id}/{image_id}/{image_id}.zarr"

    return uri


@click.command()
@click.argument("accession_id")
@click.argument("image_id")
def main(accession_id, image_id):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    zipped_zarr_rep = get_image_rep_by_type(accession_id, image_id, "zipped_zarr")
    fileref_id = zipped_zarr_rep.attributes["fileref_ids"][0]
    fileref = bia_study.file_references[fileref_id]

    path_in_zarr = zipped_zarr_rep.attributes.get("path_in_zarr", "")

    zip_fpath = stage_fileref_and_get_fpath(accession_id, fileref)

    with tempfile.TemporaryDirectory() as td:
        src_dirpath = unzip_and_get_path_of_contents(zip_fpath, td)

        uri = upload_dirpath_as_zarr_image_rep(src_dirpath, accession_id, image_id)
        uri += path_in_zarr

    rep = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=0,
        type="ome_ngff",
        uri=uri,
        dimensions=None,
        rendering=None,
        attributes={}
    )
    persist_image_representation(rep)


if __name__ == "__main__":
    main()