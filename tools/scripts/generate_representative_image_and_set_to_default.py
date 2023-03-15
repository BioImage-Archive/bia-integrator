import logging
import tempfile

import click
from bia_integrator_core.models import BIAImageRepresentation, StudyAnnotation, RenderingInfo, ChannelRendering
from bia_integrator_core.interface import persist_image_representation, persist_study_annotation
from bia_integrator_tools.utils import get_ome_ngff_rep_by_accession_and_image
from bia_integrator_tools.io import copy_local_to_s3

from preview import (
    min_dim_array_from_zarr_uri, get_single_channel_image_arrays,
    channel_arrays_and_chrenders_to_thumbnail,
    scale_channel_arrays
)

logger = logging.getLogger(__file__)


@click.command()
@click.argument('accession_id')
@click.argument('image_id')
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    dimensions = 512, 512

    ome_ngff_rep = get_ome_ngff_rep_by_accession_and_image(accession_id, image_id)
    rendering = ome_ngff_rep.rendering

    if not rendering:
        render = ChannelRendering(
            colormap_start=[0., 0., 0.],
            colormap_end=[1., 1., 1.],
            scale_factor=1
        )
        rendering=RenderingInfo(
            channel_renders=[render],
            default_t=None,
            default_z=None
        )

    channel_renders = rendering.channel_renders
    imarray = min_dim_array_from_zarr_uri(ome_ngff_rep.uri, dimensions)
    channel_arrays = get_single_channel_image_arrays(imarray, rendering.default_z, rendering.default_t)
    scaled_arrays = scale_channel_arrays(channel_arrays, channel_renders)

    im = channel_arrays_and_chrenders_to_thumbnail(scaled_arrays, channel_renders, dimensions)

    w, h = dimensions

    # im = thumbnail_from_image(accession_id, image_id, dimensions=dimensions)
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
        dimensions=str(dimensions),
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