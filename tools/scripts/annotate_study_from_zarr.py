from ast import literal_eval
import logging

import click
from bia_integrator_core.interface import load_and_annotate_study, persist_image_annotation
from bia_integrator_core.annotation import ImageAnnotation

from get_dimensions_from_bia_zarr import zarr_rep_to_dimension_annotation

logger = logging.getLogger(__file__)


def get_all_zarr_representations(bia_study):

    zarr_reps = []
    for image in bia_study.images.values():
        for rep in image.representations:
            if rep.type == "ome_ngff":
                zarr_reps.append(rep)

    return zarr_reps


@click.command()
@click.argument('accession_id')
def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    logger.info(f"Checking {len(bia_study.images)} images from {accession_id}")

    zarr_reps = get_all_zarr_representations(bia_study)
    logger.info(f"Found {len(zarr_reps)} Zarr represenations")

    for rep in zarr_reps:
        try:
            annotation = zarr_rep_to_dimension_annotation(rep)
            persist_image_annotation(annotation)
            # FIXME - this is an ugly way to do this, should parse properly somewhere else
            tdim, cdim, zdim, ydim, xdim = literal_eval(annotation.value)

            def make_and_persist_annotation(key, value):
                ann = ImageAnnotation(
                    accession_id=annotation.accession_id,
                    image_id=annotation.image_id,
                    key=key,
                    value=value
                )
                persist_image_annotation(ann)

            make_and_persist_annotation("SizeT", tdim)
            make_and_persist_annotation("SizeC", cdim)
            make_and_persist_annotation("SizeZ", zdim)
            make_and_persist_annotation("SizeY", ydim)
            make_and_persist_annotation("SizeX", xdim)
            
        except AttributeError:
            pass

    




if __name__ == main():
    main()