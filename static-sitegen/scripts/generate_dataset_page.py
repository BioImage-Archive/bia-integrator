import os
import logging
import urllib.parse

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape # type: ignore

from bia_integrator_core.integrator import load_and_annotate_study
from utils import get_annotation_images_in_study, get_non_annotation_images_in_study


logger = logging.getLogger(os.path.basename(__file__))


env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

#template = env.get_template("dataset-landing.html.j2")

DEFAULT_TEMPLATE = "dataset-landing.html.j2"


def generate_dataset_page_html(accession_id, template_fname: str):
    """Generate an HTML page for a specific dataset."""

    bia_study = load_and_annotate_study(accession_id)
    author_names = ', '.join([ 
        author.name
        for author in bia_study.authors
    ])

    image_names = {
        img.uuid: img.alias.name if img.alias else img.uuid
        for img in bia_study.images
    }

    annotation_images = get_annotation_images_in_study(bia_study)
    non_annotation_images = get_non_annotation_images_in_study(bia_study)

    ann_names = {
        img.uuid: img.alias.name if img.alias else img.uuid
        for img in annotation_images
    }

    images_with_ome_ngff = []
    image_landing_uris = {}
    image_thumbnails = {}
    image_download_uris = {}
    annotation_download_uris = {}
#    for image in bia_study.images.values():
    for image in non_annotation_images:
        for representation in image.representations:
            if representation.type == "ome_ngff":
                images_with_ome_ngff.append(image)
                image_landing_uris[image.uuid] = f"{accession_id}/{image.uuid}.html"
            if representation.type == "thumbnail":
                image_thumbnails[image.uuid] = representation.uri
            if representation.type == "fire_object":
                image_download_uris[image.uuid] = urllib.parse.quote(representation.uri, safe=":/")

    for image in annotation_images:
        for representation in image.representations:
            if representation.type == "fire_object":
                annotation_download_uris[image.uuid] = urllib.parse.quote(representation.uri, safe=":/")

    template = env.get_template(template_fname)

    rendered = template.render(
            image_names=image_names,
            study=bia_study,
            images=images_with_ome_ngff,
            landing_uris=image_landing_uris,
            image_thumbnails=image_thumbnails,
            image_download_uris=image_download_uris,
            annotation_names=annotation_images,
            ann_names=ann_names,
            annotation_download_uris=annotation_download_uris,
            non_annotation_names = non_annotation_images,
            authors=author_names
    )

    return rendered


@click.command()
@click.argument("accession_id")
@click.option("--template-fname", default=DEFAULT_TEMPLATE)
def main(accession_id: str, template_fname: str):

    logging.basicConfig(level=logging.INFO)

    rendered = generate_dataset_page_html(accession_id, template_fname)
    
    print(rendered)    


if __name__ == "__main__":
    main()