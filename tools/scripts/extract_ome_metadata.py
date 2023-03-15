import logging
import click
import json
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import BIAImage, ImageAnnotation
from bia_integrator_core.interface import persist_image_annotation

logger = logging.getLogger(__file__)


def get_image_metadata(image: BIAImage):
    largest_zarr_image = image.ome_metadata.images[0]
    first_image_metadata = json.loads(largest_zarr_image.pixels.json())

    return first_image_metadata

@click.command()
@click.argument("accession_id")
@click.argument("image_id")
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    image = bia_study.images[image_id]

    print(get_image_metadata(image))
    for k, v in get_image_metadata(image).items():
        annotation = ImageAnnotation(
            accession_id=accession_id,
            image_id=image_id,
            key=k,
            value=str(v)
        )

        persist_image_annotation(annotation)


if __name__ == "__main__":
    main()