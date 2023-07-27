import logging
import tempfile

import click
from bia_integrator_core.models import BIAImageRepresentation, StudyAnnotation, RenderingInfo, ChannelRendering
from bia_integrator_core.interface import persist_image_representation, persist_study_annotation
from bia_integrator_tools.utils import get_ome_ngff_rep_by_accession_and_image, get_example_image_uri
from bia_integrator_tools.io import copy_local_to_s3
from bia_integrator_tools.rendering import (
    NGFFProxyImage, render_proxy_image, generate_padded_thumbnail_from_ngff_uri
)

logger = logging.getLogger(__file__)


@click.command()
@click.argument('accession_id')
@click.argument('image_id')
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    # Check if there's already a representative image. If so do not overwrite.
    if get_example_image_uri(accession_id):
        logging.info(f"There is a representative image already. Terminating the script")
        return
    
    ome_ngff_rep = get_ome_ngff_rep_by_accession_and_image(accession_id, image_id)
    w = 512
    h = 512
    im = generate_padded_thumbnail_from_ngff_uri(ome_ngff_rep.uri, dims=(w,h))
    dst_key = f"{accession_id}/{image_id}/{image_id}-representative-{w}-{h}.png"

    with tempfile.NamedTemporaryFile(suffix=".png") as fh:
        im.save(fh)
        uri = copy_local_to_s3(fh.name, dst_key)
        logger.info(f"Wrote representative image to {uri}")

    rep = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=0,
        uri=uri,
        type="representative",
        dimensions=str((w, h)),
        attributes=None,
        rendering=None
    )

    persist_image_representation(rep)

    annotation = StudyAnnotation(
        accession_id=accession_id,
        key="example_image_uri",
        value=uri
    )
    persist_study_annotation(annotation)



if __name__ == "__main__":
    main()
