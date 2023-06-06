import os
import logging
import urllib.parse

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape # type: ignore

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import get_aliases
from utils import ( get_annotation_files_in_study, 
                   get_non_annotation_images_in_study,
                   add_annotation_download_size_attributes
)

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

    aliases = get_aliases(accession_id)
    aliases_by_id = {
        alias.image_id: alias.name
        for alias in aliases
    }
    image_names = {
        image_id: aliases_by_id.get(image_id, image_id)
        for image_id in bia_study.images
    }


    ann_files = get_annotation_files_in_study(bia_study)
    annotation_files = add_annotation_download_size_attributes(ann_files)

    non_annotation_images = get_non_annotation_images_in_study(bia_study)

#    ann_names = {}
#    for image in annotation_images:
#        ann_names[image.id]=aliases_by_id.get(image.id, image.id)
    

    images_with_ome_ngff = []
    images_unconverted = []
    image_landing_uris = {}
    image_thumbnails = {}
    image_download_uris = {}
    annotation_download_uris = {}
#    for image in bia_study.images.values():
    for image in non_annotation_images:
        for representation in image.representations:
            if representation.type == "ome_ngff": # or representation.type == "unconverted":
                images_with_ome_ngff.append(image)
                image_landing_uris[image.id] = f"{accession_id}/{image.id}.html"
            #if representation.type == "unconverted":
            #    images_unconverted.append(image)
            #    image_landing_uris[image.id] = f"{accession_id}/{image.id}.html"
            if representation.type == "thumbnail":
                image_thumbnails[image.id] = representation.uri
            if representation.type == "fire_object":
                image_download_uris[image.id] = urllib.parse.quote(representation.uri, safe=":/")

    for annfile in annotation_files:
        annotation_download_uris[annfile.id] = urllib.parse.quote(annfile.uri, safe=":/")

    template = env.get_template(template_fname)

    rendered = template.render(
            image_names=image_names,
            study=bia_study,
            images=images_with_ome_ngff,
            landing_uris=image_landing_uris,
            image_thumbnails=image_thumbnails,
            image_download_uris=image_download_uris,
            annotation_names=annotation_files,
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