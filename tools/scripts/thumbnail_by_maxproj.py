import logging
import tempfile

import click
from bia_integrator_core.models import BIAImageRepresentation
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


import numpy as np

from ome_zarr.io import parse_url
from ome_zarr.reader import Reader
from PIL import Image, ImageEnhance, ImageOps

logger = logging.getLogger(__file__)


def scale_to_uint8(array):

    scaled = array.astype(np.float32)

    if scaled.max() - scaled.min() == 0:
        return np.zeros(array.shape, dtype=np.uint8)

    scaled = 255 * (scaled - scaled.min()) / (scaled.max() - scaled.min())

    return scaled.astype(np.uint8)


def generate_and_persist_thumbnail_from_ngff_rep(ome_ngff_rep, dimensions):
    accession_id = ome_ngff_rep.accession_id
    image_id = ome_ngff_rep.image_id

    rendering = ome_ngff_rep.rendering

    channel_renders = ome_ngff_rep.rendering.channel_renders
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

def hacky_projection(s3_uri, image_id, accession_id, dimensions=(128, 128)):
    store = parse_url(s3_uri, mode="r").store

    reader = Reader(parse_url(s3_uri))
    # nodes may include images, labels etc
    nodes = list(reader())
    # first node will be the image pixel data
    image_node = nodes[0]

    med_res = image_node.data[1]

    ar = med_res.compute()

    zyx = ar[0,0,:,:,:]

    im = Image.fromarray(scale_to_uint8(zyx.max(axis=1)))

    enhancer = ImageEnhance.Brightness(im)

    enhanced = enhancer.enhance(2)
    dim = max(enhanced.size)
    padded = pad_to_target_dims(enhanced, (dim, dim), fill=0)

    thumbnail = padded.resize((128, 128))

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

    hacky_projection(ome_ngff_rep.uri, accession_id, image_id)

    # generate_and_persist_thumbnail_from_ngff_rep(ome_ngff_rep, dimensions   )


if __name__ == "__main__":
    main()