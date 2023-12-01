import uuid
import hashlib
import logging

from pathlib import Path

import click
import parse
from remotezip import RemoteZip

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.interface import persist_study, persist_filerefs
from bia_integrator_api.models import FileReference


FIRE_FTP_ENDPOINT = "https://ftp.ebi.ac.uk/biostudies/fire"
logger = logging.getLogger(__file__)


def zipfile_item_to_id(accession_id: str, zipfile_name: str, item_name: str):

    hash_input = accession_id
    hash_input += zipfile_name
    hash_input += item_name
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()

    id_as_uuid = uuid.UUID(version=4, hex=hexdigest)

    return str(id_as_uuid)


def get_base_http_uri_for_bst_file(accession_id: str):

    import json
    import requests

    request_uri = f"https://www.ebi.ac.uk/biostudies/api/v1/studies/{accession_id}/info"
    r = requests.get(request_uri)
    raw_obj = json.loads(r.content)

    # Strip the initial ftp from the ftp link, replace by http and add /Files
    return "https" + raw_obj["ftpLink"][3:] + "/Files"


@click.command()
@click.argument('accession_id')
@click.argument('zip_fileref_id')
def main(accession_id, zip_fileref_id):

    logging.basicConfig(level=logging.INFO)

    # base_files_uri = get_base_http_uri_for_bst_file(accession_id)

    bia_study = load_and_annotate_study(accession_id)

    dict_filerefs = {f.uuid: f for f in bia_study.file_references}
    zip_fileref = dict_filerefs[zip_fileref_id]

    if not zip_fileref.uri.endswith(".zip"):
        uri_to_fetch = zip_fileref.uri + ".zip"
    else:
        uri_to_fetch = zip_fileref.uri

    # uri = f"{base_files_uri}/{filename}"

    with RemoteZip(uri_to_fetch) as zipf:
        info_list = zipf.infolist()

    new_filerefs = []
    for item in info_list:
        if not item.filename.startswith("__MACOSX") and not item.is_dir():
            new_fileref = FileReference(
                uuid=zipfile_item_to_id(accession_id, zip_fileref.name, item.filename),
                name=item.filename,
                uri=uri_to_fetch,
                type="file_in_zip",
                size_in_bytes=item.file_size,
                attributes=zip_fileref.attributes,
                study_uuid=bia_study.uuid,
                version=0
            )

            new_filerefs.append(new_fileref)

    logger.info(f"Adding {len(new_filerefs)} new file references from archive")
    persist_filerefs(new_filerefs)

if __name__ == "__main__":
    main()
