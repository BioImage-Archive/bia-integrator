import os
import logging

import click
from jinja2 import Environment, FileSystemLoader, select_autoescape # type: ignore 

from bia_integrator_core.collection import get_collection
from bia_integrator_core.models import BIACollection
from bia_integrator_core.interface import load_and_annotate_study


logger = logging.getLogger(os.path.basename(__file__))


env = Environment(
    loader = FileSystemLoader("templates"),
    autoescape=select_autoescape()
)

DEFAULT_TEMPLATE = "collection-landing.html.j2"

def generate_collection_page_html(collection: BIACollection) -> str:

    template_fname = collection.attributes.get("collection_landing_template", DEFAULT_TEMPLATE)
    
    bia_studies = [load_and_annotate_study(accession_id) for accession_id in collection.accession_ids]

    page_suffix = collection.attributes.get("page-suffix", ".html")
    logger.info(f"Loading template {template_fname}")
    logger.info(f"Using dataset page suffix: {page_suffix}")

    template = env.get_template(template_fname)

    rendered = template.render(
            studies=bia_studies,
            collection=collection,
            page_suffix=page_suffix
    )

    return rendered


@click.command()
@click.argument("collection_name")
def main(collection_name: str):

    logging.basicConfig(level=logging.INFO)

    collection = get_collection(collection_name)
    rendered = generate_collection_page_html(collection)

    print(rendered)    


if __name__ == "__main__":
    main()