import uuid
import hashlib
import logging

from pathlib import Path

import click
import parse
from remotezip import RemoteZip

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_study
from bia_integrator_core.models import BIAFile, FileReference


FIRE_FTP_ENDPOINT = "https://ftp.ebi.ac.uk/biostudies/fire"
logger = logging.getLogger(__file__)


def zipfile_item_to_id(accession_id: str, zipfile_name: str, item_name: str):

    hash_input = accession_id
    hash_input += zipfile_name
    hash_input += item_name
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()

    id_as_uuid = uuid.UUID(version=4, hex=hexdigest)

    return str(id_as_uuid)


@click.command()
@click.argument('accession_id')
@click.argument('zip_fileref_id')
def main(accession_id, zip_fileref_id):

    logging.basicConfig(level=logging.INFO)

    result = parse.parse("{collection}{number:d}", accession_id)
    number = str(result.named['number'])
    collection = result.named['collection']
    mode = "fire"

    bia_study = load_and_annotate_study(accession_id)
    zip_fileref = bia_study.file_references[zip_fileref_id]

    base_url = "https://ftp.ebi.ac.uk/biostudies"

    uri = f"{base_url}/{mode}/{collection}/{number}/{collection}{number}/Files/{zip_fileref.name}"

    with RemoteZip(uri) as zipf:
        info_list = zipf.infolist()

    new_filerefs = {}
    for item in info_list:
        new_fileref = FileReference(
            id=zipfile_item_to_id(accession_id, zip_fileref.name, item.filename),
            name=item.filename,
            uri=uri,
            type="file_in_zip",
            size_in_bytes=item.file_size,
            attributes=zip_fileref.attributes
        )

        new_filerefs[new_fileref.id] = new_fileref

    logger.info(f"Adding {len(new_filerefs)} new file references from archive")
    bia_study.file_references.update(new_filerefs)

    persist_study(bia_study)
    


if __name__ == "__main__":
    main()
