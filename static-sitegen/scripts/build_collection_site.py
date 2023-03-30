import logging
from pathlib import Path

import click

from bia_integrator_core.collection import get_collection
from bia_integrator_core.integrator import load_and_annotate_study

from generate_collection_page import generate_collection_page_html
from generate_dataset_page import generate_dataset_page_html
from generate_image_page import generate_image_page_html


logger = logging.getLogger(__file__)


DEFAULT_DATASET_TEMPLATE = "dataset-landing.html.j2"



def generate_and_write_image_pages(accession_id, output_base_dirpath):
    bia_study = load_and_annotate_study(accession_id)
    for image in bia_study.images.values():
        for representation in image.representations:
            if representation.type == "ome_ngff":
                logger.info(f"Generating image page for {accession_id}:{image.id}")
                image_page_html = generate_image_page_html(accession_id, image.id)
                image_page_dirpath = output_base_dirpath/accession_id
                image_page_dirpath.mkdir(exist_ok=True, parents=True)
                image_page_fpath = image_page_dirpath/f"{image.id}.html"
                with open(image_page_fpath, "w") as fh:
                    fh.write(image_page_html)
    

@click.command()
@click.argument("collection_name")
def main(collection_name):
    logging.basicConfig(level=logging.INFO)

    collection = get_collection(collection_name)

    output_base_dirpath = Path("tmp/pages")
    output_base_dirpath.mkdir(exist_ok=True, parents=True)

    dataset_template_fname = collection.attributes.get(
        "dataset_landing_template", DEFAULT_DATASET_TEMPLATE
    )

    for accession_id in collection.accession_ids:
        logger.info(f"Generating dataset page for {accession_id}")
        rendered_html = generate_dataset_page_html(accession_id, dataset_template_fname)
        output_fpath = output_base_dirpath/f"{accession_id}.html"
        with open(output_fpath, "w") as fh:
            fh.write(rendered_html)

        generate_and_write_image_pages(accession_id, output_base_dirpath)

    collection_page_html = generate_collection_page_html(collection)
    collection_page_fpath = output_base_dirpath/f"{collection.name}.html"
    with open(collection_page_fpath, "w") as fh:
        fh.write(collection_page_html)

                



if __name__ == "__main__":
    main()