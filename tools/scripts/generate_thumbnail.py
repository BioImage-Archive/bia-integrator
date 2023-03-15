import logging
import tempfile

import click
from bia_integrator_core.models import BIAImageRepresentation, ChannelRendering, RenderingInfo
from bia_integrator_core.interface import persist_image_representation
from bia_integrator_tools.utils import get_ome_ngff_rep_by_accession_and_image
from bia_integrator_tools.io import copy_local_to_s3

from preview import (
    get_zarr_uri, min_dim_array_from_zarr_uri, get_single_channel_image_arrays,
    channel_render_to_cmap,
    pad_to_target_dims,
    channel_arrays_and_chrenders_to_thumbnail,
    scale_channel_arrays
)

logger = logging.getLogger(__file__)


def generate_and_persist_thumbnail_from_ngff_rep(ome_ngff_rep, dimensions):
    accession_id = ome_ngff_rep.accession_id
    image_id = ome_ngff_rep.image_id

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

    generate_and_persist_thumbnail_from_ngff_rep(ome_ngff_rep, dimensions   )


if __name__ == "__main__":
    main()