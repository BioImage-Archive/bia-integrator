import logging

import click
from ome_zarr.io import parse_url
from ome_zarr.reader import Reader
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import RenderingInfo, ChannelRendering
from bia_integrator_core.interface import persist_image_representation
from bia_integrator_tools.utils import get_ome_ngff_rep


logger = logging.getLogger(__file__)


def get_ome_ngff_rep_by_accession_and_image(accession_id: str, image_id: str) -> str:
    bia_study = load_and_annotate_study(accession_id)
    image = bia_study.images[image_id]
    
    ome_ngff_rep = get_ome_ngff_rep(image)
    
    return ome_ngff_rep


def set_rending_info_for_ome_ngff_rep(ome_ngff_rep):
    if not ome_ngff_rep.rendering:
        logger.info(f"No rendering info set, using Zarr OMERO metadata")

        reader = Reader(parse_url(ome_ngff_rep.uri))
        # nodes may include images, labels etc
        nodes = list(reader())
        # first node will be the image pixel data
        image_node = nodes[0]

        chrenders = [
            ChannelRendering(
                colormap_start=colormap_start,
                colormap_end=colormap_end
            )
            for colormap_start, colormap_end in image_node.metadata['colormap']
        ]

        ome_ngff_rep.rendering = RenderingInfo(
            channel_renders=chrenders,
            default_z=None,
            default_t=None
        )
        
        persist_image_representation(ome_ngff_rep)


@click.command()
@click.argument('accession_id')
@click.argument('image_id')
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    ome_ngff_rep = get_ome_ngff_rep_by_accession_and_image(accession_id, image_id)

    set_rending_info_for_ome_ngff_rep(ome_ngff_rep)


if __name__ == "__main__":
    main()