import logging

import click
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_image_annotation
from bia_integrator_core.models import ImageAnnotation

from bia_integrator_tools.utils import get_ome_ngff_rep
from extract_ome_metadata import get_image_metadata


@click.command()
@click.argument('accession_id')
def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    for image_id, image in bia_study.images.items():
        if image.ome_metadata:
            for k, v in get_image_metadata(image).items():
                annotation = ImageAnnotation(
                    accession_id=accession_id,
                    image_id=image_id,
                    key=k,
                    value=v
                )

                persist_image_annotation(annotation)

if __name__ == "__main__":
    main()