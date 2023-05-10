import logging
from pathlib import Path

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_image_representation
from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_tools.utils import get_image_rep_by_type
from bia_integrator_tools.io import stage_fileref_and_get_fpath, copy_local_zarr_to_s3
from bia_integrator_tools.conversion import run_zarr_conversion


logger = logging.getLogger("biaint")
logging.basicConfig(level=logging.INFO)

import typer

app = typer.Typer()


@app.command("remote-to-remote")
def convert_remote_to_remote(accession_id: str, image_id: str, rep_type: str):
    bia_study = load_and_annotate_study(accession_id)
    image_rep = get_image_rep_by_type(accession_id, image_id, rep_type)

    fileref_id = image_rep.attributes["fileref_ids"][0]
    fileref = bia_study.file_references[fileref_id]
    input_fpath = stage_fileref_and_get_fpath(accession_id, fileref)

    dst_dir_basepath = Path("tmp/c2z")/accession_id
    zarr_fpath = dst_dir_basepath/f"{image_id}.zarr"
    if not zarr_fpath.exists():
        run_zarr_conversion(input_fpath, zarr_fpath)

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

    persist_image_representation(representation)


@app.command("remote-to-local")
def convert_remote_to_local(accession_id: str, image_id: str, rep_type: str, output_dirpath: Path):
    bia_study = load_and_annotate_study(accession_id)
    image_rep = get_image_rep_by_type(accession_id, image_id, rep_type)

    for fileref_id in image_rep.attributes["fileref_ids"]:
        fileref = bia_study.file_references[fileref_id]
        input_fpath = stage_fileref_and_get_fpath(accession_id, fileref)
        run_zarr_conversion(input_fpath, output_dirpath)



if __name__ == "__main__":
    app()