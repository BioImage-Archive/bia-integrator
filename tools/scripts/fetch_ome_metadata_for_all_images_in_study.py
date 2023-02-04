import logging

import click
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_image_annotation
from bia_integrator_core.models import ImageAnnotation

from bia_integrator_tools.utils import get_ome_ngff_rep
from extract_ome_metadata import image_metadata_from_zarr_uri


@click.command()
@click.argument('accession_id')
def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    for image_id, image in bia_study.images.items():
        ngff_rep = get_ome_ngff_rep(image)

        if ngff_rep:
            first_image_metadata = image_metadata_from_zarr_uri(ngff_rep.uri)

            for k, v in first_image_metadata.items():
                annotation = ImageAnnotation(
                    accession_id=accession_id,
                    image_id=image_id,
                    key=k,
                    value=v
                )

                persist_image_annotation(annotation)


if __name__ == "__main__":
    main()