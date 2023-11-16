import logging
import tempfile

import click
from bia_integrator_core.interface import persist_image_representation, api_models
from bia_integrator_tools.utils import ( get_ome_ngff_rep_by_accession_and_image, 
)
from bia_integrator_tools.io import copy_local_to_s3


from bia_integrator_tools.rendering import generate_padded_thumbnail_from_ngff_uri


logger = logging.getLogger(__file__)


def generate_and_persist_thumbnail_from_ngff_rep(ome_ngff_rep, accession_id, image_uuid, dimensions):

    # Use first URI - assume this is OK for generating thumbnails if more than
    # one URI exists.
    im = generate_padded_thumbnail_from_ngff_uri(ome_ngff_rep.uri[0])
    w, h = dimensions

    dst_key = f"{accession_id}/{image_uuid}/{image_uuid}-thumbnail-{w}-{h}.png"

    with tempfile.NamedTemporaryFile(suffix=".png") as fh:
        im.save(fh)
        thumbnail_uri = copy_local_to_s3(fh.name, dst_key)
        logger.info(f"Wrote thumbnail to {thumbnail_uri}")

    rep = api_models.BIAImageRepresentation(
        size=0,
        uri=[thumbnail_uri,],
        type="thumbnail",
        dimensions=str(dimensions),
        attributes=None,
        rendering=None
    )

    persist_image_representation(image_uuid, rep)

@click.command()
@click.argument('accession_id')
@click.argument('image_uuid')
def main(accession_id, image_uuid):

    logging.basicConfig(level=logging.INFO)

    dimensions = 128, 128

    ome_ngff_rep = get_ome_ngff_rep_by_accession_and_image(accession_id, image_uuid)

    generate_and_persist_thumbnail_from_ngff_rep(ome_ngff_rep, accession_id, image_uuid, dimensions)


if __name__ == "__main__":
    main()
