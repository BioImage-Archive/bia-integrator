"""Select the first n number of images of a study to convert to ome-ngff."""

import logging

import click

from bia_integrator_core.integrator import load_and_annotate_study


logger = logging.getLogger(__file__)

@click.command()
@click.argument('accession_id')
@click.argument('number_of_images')
def main(accession_id,number_of_images):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    image_ids = list(bia_study.images.keys())
    n = int(number_of_images)
    print('\n'.join(image_ids[:n]))

if __name__ == "__main__":
    main()