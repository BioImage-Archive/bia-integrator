import logging

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.io import stage_fileref_and_get_fpath

import typer


app = typer.Typer()


logger = logging.getLogger(__file__)


@app.command("stage")
def stage_fileref_to_local(accession_id: str, fileref_id: str):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    fileref = bia_study.file_references[fileref_id]

    local_fpath = stage_fileref_and_get_fpath(accession_id, fileref)

    print(local_fpath)


if __name__ == "__main__":
    app()