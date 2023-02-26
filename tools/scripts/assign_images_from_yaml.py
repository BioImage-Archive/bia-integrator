import uuid
import hashlib
import logging


import click
from ruamel.yaml import YAML

from bia_integrator_core.models import BIAImage, BIAImageRepresentation
from bia_integrator_core.interface import persist_image
from bia_integrator_core.integrator import load_and_annotate_study


logger = logging.getLogger(__file__)


@click.command()
@click.argument("yaml_fpath")
def main(yaml_fpath):
    logging.basicConfig(level=logging.INFO)

    yaml = YAML()
    with open(yaml_fpath) as fh:
        raw_config = yaml.load(fh)

    accession_id = raw_config['accession_id']
    bia_study = load_and_annotate_study(accession_id)

    for image_description in raw_config['images'].values():
        name = image_description['name']
        fileref_ids = image_description['fileref_ids']

        hash_input = ''.join(fileref_ids)
        hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()
        image_id_as_uuid = uuid.UUID(version=4, hex=hexdigest)
        image_id = str(image_id_as_uuid)

        filerefs = [bia_study.file_references[id] for id in fileref_ids]

        image_rep = BIAImageRepresentation(
            accession_id=accession_id,
            image_id=image_id,
            size=sum(fileref.size_in_bytes for fileref in filerefs),
            uri=[fileref.uri for fileref in filerefs],
            attributes={"fileref_ids": fileref_ids},
            type="multi_fileref"
        )

        image = BIAImage(
            id=image_id,
            accession_id=accession_id,
            original_relpath=name,
            name=name,
            representations=[image_rep]
        )

        persist_image(image)


if __name__ == "__main__":
    main()