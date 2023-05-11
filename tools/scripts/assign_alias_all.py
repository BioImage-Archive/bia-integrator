import click
import logging

from bia_integrator_core.models import BIAImageAlias
from bia_integrator_core.config import settings
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import (
    get_image_annotations,
    persist_image_annotation,
    get_representations,
    persist_image_representation,
    persist_image_alias
)

from bia_integrator_tools.biostudies import load_submission

from assign_single_image_from_fileref import create_and_persist_image_from_fileref
from ingest_from_biostudies import filerefs_from_bst_submission


logger = logging.getLogger(__file__)


@click.command()
@click.argument('accession_id')

def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    i = 1
    for image_id, image in bia_study.images.items():

        al_id = "IM"+str(i) 
        alias = BIAImageAlias(
                accession_id=accession_id,
                name=al_id,
                image_id=image_id
            )
        persist_image_alias(alias)
        i+=1


if __name__ == "__main__":
    main()