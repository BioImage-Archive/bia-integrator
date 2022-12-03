import os
import logging

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape

from bia_integrator_core.integrator import load_and_annotate_study


logger = logging.getLogger(os.path.basename(__file__))


env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

template = env.get_template("image-landing.html.j2")


def generate_image_page_html(accession_id, image_id):

    bia_study = load_and_annotate_study(accession_id)
    bia_image = bia_study.images[image_id]

    reps_by_type = {
        representation.type: representation
        for representation in bia_image.representations
    }

    rendered = template.render(study=bia_study, image=bia_image, zarr_uri=reps_by_type["ome_ngff"].uri)

    return rendered


@click.command()
@click.argument("accession_id")
@click.argument("image_id")
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    rendered = generate_image_page_html(accession_id, image_id)

    print(rendered)




if __name__ == "__main__":
    main()