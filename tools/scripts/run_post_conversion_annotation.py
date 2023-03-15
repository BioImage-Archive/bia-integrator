import logging

import click

from bia_integrator_core.integrator import load_and_annotate_study

from bia_integrator_tools.utils import set_rendering_info_for_ome_ngff_rep

from generate_thumbnail import generate_and_persist_thumbnail_from_ngff_rep


logger = logging.getLogger(__file__)


@click.command()
@click.argument("accession_id")
def main(accession_id):
    logging.basicConfig(level=logging.INFO)

    dimensions = 128, 128

    bia_study = load_and_annotate_study(accession_id)

    for image_id, image in bia_study.images.items():
        for rep in image.representations:
            if rep.type == "ome_ngff":
                try:
                    set_rendering_info_for_ome_ngff_rep(rep)
                    generate_and_persist_thumbnail_from_ngff_rep(rep, dimensions)
                except AttributeError:
                    pass


if __name__ == "__main__":
    main()