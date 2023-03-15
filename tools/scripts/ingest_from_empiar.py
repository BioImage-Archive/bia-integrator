import json
import uuid
import hashlib
import logging
import pathlib
from typing import Optional, Dict

import click
import requests
from fs.ftpfs import FTPFS
from pydantic import BaseModel
import fsspec.implementations.ftp

from bia_integrator_core.models import FileReference, BIAStudy, Author
from bia_integrator_core.interface import persist_study


logger = logging.getLogger(__file__)


class EMPIARFile(BaseModel):
    path: pathlib.Path
    size: int


class EMPIARAuthor(BaseModel):
    
    name: str
    author_orcid: Optional[str]


def parse_empiar_authors(raw_obj):
    entry_dict = list(raw_obj.values())[0]
    author_dictlist = entry_dict['authors']
    authors = [EMPIARAuthor.parse_obj(entry['author']) for entry in author_dictlist]
    return authors


def empiar_file_to_id(accession_id: str, file: EMPIARFile) -> str:

    hash_input = accession_id
    hash_input += str(file.path)
    hash_input += str(file.size)
    hexdigest = hashlib.md5(hash_input.encode("utf-8")).hexdigest()

    id_as_uuid = uuid.UUID(version=4, hex=hexdigest)

    return str(id_as_uuid)


def empiar_file_uri(accession_id, file: EMPIARFile) -> str:

    base_uri = "https://ftp.ebi.ac.uk"
    accession_no = accession_id.split("-")[1]
    root_path = f"/empiar/world_availability/{accession_no}/data"

    return f"{base_uri}{root_path}/{file.path}"


def empiar_file_to_file_reference(accession_id: str, file: EMPIARFile) -> FileReference:

    fileref_id = empiar_file_to_id(accession_id, file)
    fileref_name = str(file.path)

    fileref = FileReference(
        id=fileref_id,
        name=fileref_name,
        uri=empiar_file_uri(accession_id, file),
        size_in_bytes=file.size,
        attributes={}
    )

    return fileref


def fsspec_stats_to_empiar_file(stats: Dict) -> EMPIARFile:
    empiar_file = EMPIARFile(
        path=stats['name'],
        size=stats['size']
    )    

    return empiar_file


def empiar_files_by_fssspec(accession_no):

    ftpfs = fsspec.implementations.ftp.FTPFileSystem("ftp.ebi.ac.uk")

    file_list = ftpfs.find(f'/empiar/world_availability/{accession_no}/data')
    stats_list = [ftpfs.stat(fpath) for fpath in file_list]
    empiar_files = [fsspec_stats_to_empiar_file(stats) for stats in stats_list]

    return empiar_files


def empiar_files_by_pyfilesystem(accession_no: str):

    ftp_fs = FTPFS('ftp.ebi.ac.uk')
    root_path = f"/empiar/world_availability/{accession_no}/data"
    walker = ftp_fs.walk(root_path)

    empiar_files = []

    for path, dirs, files in walker:
        for file in files:
            relpath = pathlib.Path(path).relative_to(root_path)
            empiar_file = EMPIARFile(
                path=relpath/file.name,
                size=file.size
            )
            empiar_files.append(empiar_file)

    return empiar_files


def generate_filerefs_for_empiar_entry(accession_no: str):

    empiar_files = empiar_files_by_pyfilesystem(accession_no)

    accession_id = f"EMPIAE-{accession_no}"
    filerefs = [
        empiar_file_to_file_reference(accession_id, empiar_file)
        for empiar_file in empiar_files
    ]

    return filerefs


@click.command()
@click.argument('accession_id')
def main(accession_id):
    logging.basicConfig(level=logging.INFO)

    accession_no = accession_id.split("-")[1]
    logger.info(f"Generating study for EMPIAR entry {accession_no}")
    empiar_uri = f"https://www.ebi.ac.uk/empiar/api/entry/{accession_no}"

    r = requests.get(empiar_uri)
    raw_data = json.loads(r.content)
    empiar_authors = parse_empiar_authors(raw_data)
    filerefs = generate_filerefs_for_empiar_entry(accession_no)

    bia_study = BIAStudy(
        accession_id=accession_id,
        release_date=raw_data[accession_id]['release_date'],
        title=raw_data[accession_id]['title'],
        description=raw_data[accession_id]['title'],
        organism="Unknown",
        imaging_type="Unknown",
        file_references={fileref.id: fileref for fileref in filerefs},
        authors = [Author.parse_obj(a.__dict__) for a in empiar_authors]
    )

    persist_study(bia_study)


if __name__ == "__main__":
    main()