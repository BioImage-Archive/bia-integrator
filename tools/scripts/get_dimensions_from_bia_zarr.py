import logging

import click

from ome_zarr.utils import info
from ome_zarr.io import parse_url
from ome_zarr.reader import Multiscales, Node, Reader
from bia_integrator_core.interface import get_image, persist_image_annotation, api_models
from bia_integrator_core.config import settings

logger = logging.getLogger(__file__)


def zarr_rep_to_dimension_annotation(zarr_rep: api_models.BIAImageRepresentation) -> api_models.ImageAnnotation:
    """For the given Zarr representation, find the dimensions of the largest array,
    create an annotation using the string representation of these dimensions and return."""

    logger.info(f"Loading from {zarr_rep.uri}")

    zarr = parse_url(zarr_rep.uri[0])
    reader = Reader(zarr)

    nodes = [node for node in reader()]
    assert len(nodes) == 1, "Zarr contains multiple images"

    shapes = [array.shape for array in nodes[0].data]
    original_image_dim = shapes[0]

    annotation = api_models.ImageAnnotation(
        author_email=settings.bia_username,
        key="dimensions",
        value=str(original_image_dim),
        state="active"
    )

    return annotation


@click.command()
@click.argument("accession_id")
@click.argument("image_uuid")
def main(accession_id, image_uuid):

    logging.basicConfig(level=logging.INFO)

    image = get_image(accession_id, image_uuid)
    reps_by_type = {
        rep.type: rep
        for rep in image.representations
    }

    annotation = zarr_rep_to_dimension_annotation(reps_by_type["ome_ngff"])
    persist_image_annotation(image_uuid, annotation)


if __name__ == "__main__":
    main()