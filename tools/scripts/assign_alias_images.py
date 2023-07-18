"""Assign aliases to all images in a study. Needs update for zips"""
 
import click
import logging

from bia_integrator_core.models import BIAImageAlias
from bia_integrator_core.config import settings
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import (
    persist_image_alias,
    get_aliases
)

logger = logging.getLogger(__file__)


@click.command()
@click.argument('accession_id')

def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    all_aliases = get_aliases(accession_id)
    # check if there is any image aliases, if not, go through the list and assign all images, assuming they're not zipped:
    if not all_aliases:
        i = 1
        for image_id in bia_study.images.keys():
            al_id = "IM"+str(i) 
            alias = BIAImageAlias(
                    accession_id=accession_id,
                    name=al_id,
                    image_id=image_id
                )
            persist_image_alias(alias)
            i+=1
    else:
        all_image_ids = {fr.imageid: fr for fr in all_aliases}
        last_alias = len(all_image_ids)
        for image_id in bia_study.images.keys():
            if not image_id in all_image_ids.keys():
                # TO CHECK
                # how to assign alias for studies that have *some* images with aliases and some without
                al_id = "IM" + str(last_alias + 1)
                alias = BIAImageAlias(
                    accession_id=accession_id,
                    name=al_id,
                    image_id=image_id
                    )
                persist_image_alias(alias)
                last_alias +=1

