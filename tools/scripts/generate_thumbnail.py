import logging
import tempfile

import click
from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.interface import persist_image_representation
from bia_integrator_tools.utils import ( get_ome_ngff_rep_by_accession_and_image, 
                                        get_unconverted_rep_by_accession_and_image
)
from bia_integrator_tools.io import copy_local_to_s3


from bia_integrator_tools.rendering import generate_padded_thumbnail_from_ngff_uri


logger = logging.getLogger(__file__)


def generate_and_persist_thumbnail_from_ngff_rep(ome_ngff_rep, dimensions):

    accession_id = ome_ngff_rep.accession_id
    image_id = ome_ngff_rep.image_id

    im = generate_padded_thumbnail_from_ngff_uri(ome_ngff_rep.uri)
    w, h = dimensions

    dst_key = f"{accession_id}/{image_id}/{image_id}-thumbnail-{w}-{h}.png"

    with tempfile.NamedTemporaryFile(suffix=".png") as fh:
        im.save(fh)
        thumbnail_uri = copy_local_to_s3(fh.name, dst_key)
        logger.info(f"Wrote thumbnail to {thumbnail_uri}")

    rep = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=0,
        uri=thumbnail_uri,
        type="thumbnail",
        dimensions=str(dimensions),
        attributes=None,
        rendering=None
    )

    persist_image_representation(rep)

def generate_and_persist_thumbnail_from_im_rep(im_rep, dimensions):
    accession_id = im_rep.accession_id
    image_id = im_rep.image_id

    im = thumbnail_from_unconverted_image(accession_id, image_id, dimensions)

    w, h = dimensions

    dst_key = f"{accession_id}/{image_id}/{image_id}-thumbnail-{w}-{h}.png"

    with tempfile.NamedTemporaryFile(suffix=".png") as fh:
        im.save(fh)
        thumbnail_uri = copy_local_to_s3(fh.name, dst_key)
        logger.info(f"Wrote thumbnail to {thumbnail_uri}")

    rep = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=0,
        uri=thumbnail_uri,
        type="thumbnail",
        dimensions=str(dimensions),
        attributes=None,
        rendering=None
    )

    persist_image_representation(rep)

@click.command()
@click.argument('accession_id')
@click.argument('image_id')
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    dimensions = 128, 128

    ome_ngff_rep = get_ome_ngff_rep_by_accession_and_image(accession_id, image_id)

    generate_and_persist_thumbnail_from_ngff_rep(ome_ngff_rep, dimensions)


if __name__ == "__main__":
    main()