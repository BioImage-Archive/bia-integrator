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

# Attributes to display in study content section
# Use list for backward compatibility with different annotation names
# Most recent names come first in list
STUDY_CONTENT_ANNOTATIONS = {
    "Study size:": ["study_size_human_readable", "study_size"],
    "N files (exc zip contents):": ["n_files_excluding_zip_contents", "n_files_in_study",],
    "N files (inc zip contents):": ["n_files_including_zip_contents",],
    "Filetype breakdown:": ["filetype_breakdown_html",],
}

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


    an_aliases_by_name = {
        annfile.name: annfile.attributes['alias'] 
        for annfile in annotation_files
        }

    ann_aliases_for_images = {
        image.id: an_aliases_by_name.get(image.name)
        for image in bia_study.images.values()
    }     
    

    images_with_ome_ngff = []
    image_landing_uris = {}
    image_thumbnails = {}
    image_download_uris = {}
    annotation_download_uris = {}
    for image in bia_study.images.values():
        for representation in image.representations:
            if representation.type == "ome_ngff": 
                images_with_ome_ngff.append(image)
                image_landing_uris[image.id] = f"{accession_id}/{image.id}.html"
            if representation.type == "thumbnail":
                image_thumbnails[image.id] = representation.uri
            if representation.type in ["fire_object", "zipped_zarr"]:
                image_download_uris[image.id] = urllib.parse.quote(representation.uri, safe=":/")

    for annfile in annotation_files:
        annotation_download_uris[annfile.id] = urllib.parse.quote(annfile.uri, safe=":/")

    template = env.get_template(template_fname)

    # Get the keys to use for rendering study contents section
    study_content_annotations = {}
    for label, keys in STUDY_CONTENT_ANNOTATIONS.items():
        for key in keys:
            if key in bia_study.attributes:
                study_content_annotations[label] = key
                break

    rendered = template.render(
            image_names=image_names,
            study=bia_study,
            images=images_with_ome_ngff,
            landing_uris=image_landing_uris,
            image_thumbnails=image_thumbnails,
            image_download_uris=image_download_uris,
            annotation_names=annotation_files,
            annotation_download_uris=annotation_download_uris,
            authors=author_names,
            study_content_annotations=study_content_annotations,
            image_ann_aliases=ann_aliases_for_images
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
