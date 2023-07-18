"""Select images in a study for which we know how to convert
the image. This is evaluated by looking through a list of known good file extensions."""

import logging


from pathlib import Path

import click

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.utils import create_and_persist_image_from_fileref


logger = logging.getLogger(__file__)


@click.command()
@click.argument("accession_id")
def main(accession_id):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    convertable_ext_path = Path(__file__).resolve().parent.parent / "resources" /"bioformats_curated_single_file_formats.txt"

    easily_convertable_exts = [ l for l in convertable_ext_path.read_text().split("\n") if len(l) > 0]
    for image in bia_study.images.values():
        if Path(image.name).suffix.lower() in easily_convertable_exts:
            print(str(image.id))



if __name__ == "__main__":
    main()