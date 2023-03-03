import logging
from typing import Optional

from ome_zarr.io import parse_url
from ome_zarr.reader import Reader
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.models import RenderingInfo, ChannelRendering
from bia_integrator_core.interface import persist_image_representation

logger = logging.getLogger(__name__)


def get_image_rep_by_type(accession_id, image_id, rep_type):

    bia_study = load_and_annotate_study(accession_id)

    for image_rep in bia_study.images[image_id].representations:
        if image_rep.type == rep_type:
            return image_rep

    return None


def get_ome_ngff_rep(image):
    for rep in image.representations:
        if rep.type == "ome_ngff":
            return rep


def get_ome_ngff_rep_by_accession_and_image(accession_id: str, image_id: str) -> Optional[BIAImageRepresentation]:
    bia_study = load_and_annotate_study(accession_id)
    image = bia_study.images[image_id]
    
    ome_ngff_rep = get_ome_ngff_rep(image)
    
    return ome_ngff_rep


def set_rendering_info_for_ome_ngff_rep(ome_ngff_rep):
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