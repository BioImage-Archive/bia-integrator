import os
import uuid
import logging
import tempfile
from pathlib import Path

import click
import shutil
import requests
from pydantic import BaseSettings


from bia_integrator_tools.conversion import run_zarr_conversion
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.interface import persist_image_representation
from bia_integrator_tools.utils import get_image_rep_by_type
from bia_integrator_tools.io import stage_fileref_and_get_fpath, c2zsettings


logger = logging.getLogger(__file__)


@click.command()
@click.argument("accession_id")
@click.argument("image_id")
@click.argument("output_fpath")
def main(accession_id, image_id, output_fpath):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    rep = get_image_rep_by_type(accession_id, image_id, "fire_object")
    fileref_id = rep.attributes["fileref_ids"][0]
    fileref = bia_study.file_references[fileref_id]
    input_fpath = stage_fileref_and_get_fpath(accession_id, fileref)

    run_zarr_conversion(input_fpath, output_fpath)





if __name__ == "__main__":
    main()