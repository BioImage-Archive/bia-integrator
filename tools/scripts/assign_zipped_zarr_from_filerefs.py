import uuid
import logging
import hashlib

import click
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import BIAImage, BIAImageRepresentation
from bia_integrator_core.image import persist_image

logger = logging.getLogger(__file__)


@click.command()
@click.argument("accession_id")
def main(accession_id):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)

    filerefs = bia_study.file_references

    for fileref in filerefs.values():
        name = fileref.name.split('.', maxsplit=1)[0]

        hash_input = fileref.id
        hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
        image_id_as_uuid = uuid.UUID(version=4, hex=hexdigest)
        image_id = str(image_id_as_uuid)

        image_rep = BIAImageRepresentation(
            accession_id=accession_id,
            image_id=image_id,
            size=fileref.size_in_bytes,
            uri=fileref.uri,
            attributes={
                "fileref_ids": [fileref.id],
                "path_in_zarr": "/0"
            },
            type="zipped_zarr"
        )

        image = BIAImage(
            id=image_id,
            accession_id=accession_id,
            original_relpath=name,
            name=name,
            representations=[image_rep],
            attributes=fileref.attributes
        )

        persist_image(image)


if __name__ == "__main__":
    main()