import os
import logging

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape # type: ignore 

from bia_integrator_core.collection import get_collection
from bia_integrator_core.models import BIACollection
from bia_integrator_core.interface import load_and_annotate_study
from utils import ( get_annotation_files_in_study, 
                   get_non_annotation_images_in_study)

logger = logging.getLogger(os.path.basename(__file__))

env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

DEFAULT_TEMPLATE = "galleries-landing.html.j2"

def generate_galleries_landing_page_html(collections: list[BIACollection]) -> str:

    template_fname = DEFAULT_TEMPLATE
    page_suffix = ".html"
    logger.info(f"Loading template {template_fname}")
    logger.info(f"Using page suffix: {page_suffix}")

    template = env.get_template(template_fname)

    rendered = template.render(
            collections=collections,
            page_suffix=page_suffix
    )

    return rendered


@click.command()
@click.argument("collection_names")
def main(collection_names: str):

    logging.basicConfig(level=logging.INFO)
    collections = []
    for collection_name in collection_names.split(","):
        collections.append(get_collection(collection_name))
    
    rendered = generate_galleries_landing_page_html(collections)

    print(rendered)    

if __name__ == "__main__":
    main()
