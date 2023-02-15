import os
import logging
import urllib.parse

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape # type: ignore

from bia_integrator_core.integrator import load_and_annotate_study


logger = logging.getLogger(os.path.basename(__file__))


env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

template = env.get_template("dataset-landing.html.j2")


def generate_dataset_page_html(accession_id):
    bia_study = load_and_annotate_study(accession_id)
    author_names = ', '.join([ 
        author.name
        for author in bia_study.authors
    ])

    images_with_ome_ngff = []
    image_landing_uris = {}
    image_thumbnails = {}
    image_download_uris = {}
    for image in bia_study.images.values():
        for representation in image.representations:
            if representation.type == "ome_ngff":
                images_with_ome_ngff.append(image)
                image_landing_uris[image.id] = f"{accession_id}/{image.id}.html"
            if representation.type == "thumbnail":
                image_thumbnails[image.id] = representation.uri
            if representation.type == "fire_object":
                image_download_uris[image.id] = urllib.parse.quote(representation.uri, safe=":/")

    rendered = template.render(
            study=bia_study,
            images=images_with_ome_ngff,
            landing_uris=image_landing_uris,
            image_thumbnails=image_thumbnails,
            image_download_uris=image_download_uris,
            authors=author_names
    )

    return rendered


@click.command()
@click.argument("accession_id")
def main(accession_id):

    logging.basicConfig(level=logging.INFO)

    rendered = generate_dataset_page_html(accession_id)
    
    print(rendered)    


if __name__ == "__main__":
    main()