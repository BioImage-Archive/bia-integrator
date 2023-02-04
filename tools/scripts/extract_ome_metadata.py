import logging
from pathlib import Path
from typing import List
from urllib.parse import urlparse, urlunparse
import xml.etree.ElementTree as ET

import click
import requests
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import ImageAnnotation
from bia_integrator_core.interface import persist_image_annotation

from bia_integrator_tools.utils import get_ome_ngff_rep


logger = logging.getLogger(__file__)


def image_metadata_from_zarr_uri(uri):

    parsed_url = urlparse(uri)
    ome_metadata_path = Path(parsed_url.path).parent/"OME/METADATA.ome.xml"

    ome_metadata_uri = urlunparse((parsed_url.scheme, parsed_url.netloc, str(ome_metadata_path), None, None, None))
    logger.info(f"Fetching OME metadata from {ome_metadata_uri}")

    r = requests.get(ome_metadata_uri)
    assert r.status_code == 200
    root = ET.fromstring(r.content)
    xml_namespace = list(root.attrib.values())[0].split()[0]

    def ns_element(name):
        return "{{{}}}{}".format(xml_namespace, name)

    metadata_by_image_name = {}
    for element in root.findall(ns_element("Image")):
        image_name = element.attrib['Name']
        pixels_element = element.find(ns_element("Pixels"))
        image_data = pixels_element.attrib
        metadata_by_image_name[image_name] = image_data

    logger.info(f"Found metadata: {metadata_by_image_name.values()}")

    # Pyramidal files sometimes have multiple "Images", we pick the first one and hope this is biggest
    # TODO: Make sure it is!

    first_image_metadata = list(metadata_by_image_name.values())[0]
    logger.info(f"Metadata for first image: {first_image_metadata}")

    return first_image_metadata


@click.command()
@click.argument("accession_id")
@click.argument("image_id")
def main(accession_id, image_id):

    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    image = bia_study.images[image_id]

    ngff_rep = get_ome_ngff_rep(image)

    first_image_metadata = image_metadata_from_zarr_uri(ngff_rep.uri)

    for k, v in first_image_metadata.items():
        annotation = ImageAnnotation(
            accession_id=accession_id,
            image_id=image_id,
            key=k,
            value=v
        )

        persist_image_annotation(annotation)


if __name__ == "__main__":
    main()