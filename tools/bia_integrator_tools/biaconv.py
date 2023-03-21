import logging
from pathlib import Path

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.utils import get_image_rep_by_type
from bia_integrator_tools.io import stage_fileref_and_get_fpath
from bia_integrator_tools.conversion import run_zarr_conversion

logger = logging.getLogger("biaint")
logging.basicConfig(level=logging.INFO)

import typer

app = typer.Typer()


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