"""Assign images from zipped ome.zarr file references."""

import logging

import click
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.utils import create_and_persist_image_from_fileref

logger = logging.getLogger(__file__)


@click.command()
@click.argument("accession_id")
def main(accession_id):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    filerefs = bia_study.file_references

    for fileref in filerefs:
        if ".zarr" in fileref.name:
            create_and_persist_image_from_fileref(
                bia_study.uuid,
                fileref,
                rep_type="zipped_zarr", 
                extra_attributes = {"path_in_zarr": "/0"}
            )


if __name__ == "__main__":
    main()
