import logging

import click


from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.utils import create_and_persist_image_from_fileref


logger = logging.getLogger(__file__)


@click.command()
@click.argument("accession_id")
@click.argument("fileref_id")
def main(accession_id, fileref_id):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    fileref = bia_study.file_references[fileref_id]


    create_and_persist_image_from_fileref(accession_id, fileref)


        


if __name__ == "__main__":
    main()