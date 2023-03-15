import uuid
import logging
import hashlib

import click

from bia_integrator_core.models import BIAImage, BIAImageRepresentation
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.image import persist_image


logger = logging.getLogger(__file__)


def create_and_persist_image_from_fileref(accession_id, fileref):
    name = fileref.name
    logger.info(f"Assigned name {name}")

    hash_input = fileref.id
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
    image_id_as_uuid = uuid.UUID(version=4, hex=hexdigest)
    image_id = str(image_id_as_uuid)

    image_rep = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        size=fileref.size_in_bytes,
        uri=fileref.uri,
        attributes={"fileref_ids": [fileref.id]},
        type="fire_object"
    )

    image = BIAImage(
        id=image_id,
        accession_id=accession_id,
        original_relpath=name,
        name=name,
        representations=[image_rep]
    )

    persist_image(image)

    return image_id


@click.command()
@click.argument("accession_id")
@click.argument("fileref_id")
def main(accession_id, fileref_id):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    fileref = bia_study.file_references[fileref_id]


    create_and_persist_image_from_fileref(accession_id, fileref)


        


if __name__ == "__main__":
    main()