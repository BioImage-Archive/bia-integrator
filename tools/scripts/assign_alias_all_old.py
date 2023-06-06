"""Assign aliases to all images and annotations in a study. Needs update for zips"""

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
        j = 1
        for image_id, image in bia_study.images.items():
            if image.attributes.get('source image'): 
                al_id = "AN"+str(i)
                i += 1
            else:
                al_id = "IM"+str(j)
                j += 1 
            alias = BIAImageAlias(
                    accession_id=accession_id,
                    name=al_id,
                    image_id=image_id
                )
            persist_image_alias(alias)
            
    else:
        all_image_ids = {fr.imageid: fr for fr in all_aliases}
        an_aliases = []
        im_aliases = []
        for fr in all_aliases:
            if fr.name.startswith('AN'):
                an_aliases.append(fr.name)
            elif fr.name.startswith('IM'):
                im_aliases.append(fr.name)
        last_an_alias = len(an_aliases)
        last_im_alias = len(im_aliases)
        for image_id, image in bia_study.images.items():
            if not image_id in all_image_ids.keys():
                # TO CHECK
                # how to assign alias for studies that have *some* images with aliases and some without
                if image.attributes.get('source image'): 
                    al_id = "AN"+ str(last_an_alias + 1)
                    last_an_alias +=1
                else:
                    al_id = "IM"+ str(last_im_alias + 1)
                    last_im_alias +=1
                alias = BIAImageAlias(
                    accession_id=accession_id,
                    name=al_id,
                    image_id=image_id
                    )
                persist_image_alias(alias)



if __name__ == "__main__":
    main()