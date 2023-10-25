"""Assign aliases to all images in a study. Needs update for zips"""
 
import click
import logging

from bia_integrator_api.models import BIAImageAlias
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import update_image, get_images

logger = logging.getLogger(__file__)


@click.command()
@click.argument('accession_id')

def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    images = get_images(accession_id)
    # check if there is any image aliases, if not, go through the list and assign all images, assuming they're not zipped:
    assigned_aliases = [image.alias.name for image in images if image.alias]
    if not assigned_aliases:
        for alias_counter, image in enumerate(images, start=1):
            image.alias = BIAImageAlias(name=f"IM{alias_counter}")
            update_image(image)
    else:
        alias_counter = 1
        for image in images:
            if image.alias:
                continue
            while True:
                alias = f"IM{alias_counter}"
                if alias in assigned_aliases:
                    alias_counter += 1
                else:
                    break
            image.alias = BIAImageAlias(name=alias)
            assigned_aliases.append(alias)
            update_image(image)

if __name__ == "__main__":
    main()