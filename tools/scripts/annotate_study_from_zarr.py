from ast import literal_eval
import logging

import click
from bia_integrator_core.interface import load_and_annotate_study, persist_image_annotation, api_models
from bia_integrator_core.config import settings

from get_dimensions_from_bia_zarr import zarr_rep_to_dimension_annotation
from get_axis_names_from_bia_zarr import zarr_rep_to_axis_names_annotation

logger = logging.getLogger(__file__)


def get_all_zarr_representations(bia_study):

    zarr_reps = []
    for image in bia_study.images:
        for rep in image.representations:
            if rep.type == "ome_ngff":
                zarr_reps.append((image.uuid, rep))

    return zarr_reps


@click.command()
@click.argument('accession_id')
def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    logger.info(f"Checking {len(bia_study.images)} images from {accession_id}")

    zarr_reps = get_all_zarr_representations(bia_study)
    logger.info(f"Found {len(zarr_reps)} Zarr represenations")

    for image_uuid, rep in zarr_reps:
        try:
            dims_annotation = zarr_rep_to_dimension_annotation(rep)
            persist_image_annotation(image_uuid, dims_annotation)
            # FIXME - this is an ugly way to do this, should parse properly somewhere else
            dims_tuple = literal_eval(dims_annotation.value)
            
            axis_names_annotation = zarr_rep_to_axis_names_annotation(rep)
            persist_image_annotation(image_uuid, axis_names_annotation)
            # FIXME - this is an ugly way to do this, should parse properly somewhere else
            axis_names_tuple = literal_eval(axis_names_annotation.value)

            def make_and_persist_annotation(key, value):
                ann = api_models.ImageAnnotation(
                    author_email=settings.bia_username,
                    key=key,
                    value=str(value),
                    state="active"
                )
                persist_image_annotation(image_uuid, ann)
            
            if len(dims_tuple) == len(axis_names_tuple):
                # Try to create dims annotations using axes names
                for name, value in zip(axis_names_tuple, dims_tuple):
                    key = f"Size{name.upper()[0]}"
                    make_and_persist_annotation(key, value)
            else:
                # Otherwise use implicit exptectation of t,c,z,y,x order
                # Create default values for dims
                zdim = 1
                ydim = 1
                xdim = 1

                if len(dims_tuple) == 5:
                    tdim, cdim, zdim, ydim, xdim = dims_tuple
                    make_and_persist_annotation("SizeT", tdim)
                    make_and_persist_annotation("SizeC", cdim)
                if len(dims_tuple) == 3 or len(dims_tuple) == 4:
                    zdim, ydim, xdim = dims_tuple[-3:]
                if len(dims_tuple) == 2:
                    ydim, xdim = dims_tuple

                make_and_persist_annotation("SizeZ", zdim)
                make_and_persist_annotation("SizeY", ydim)
                make_and_persist_annotation("SizeX", xdim)
            
        except AttributeError:
            pass

if __name__ == main():
    main()
