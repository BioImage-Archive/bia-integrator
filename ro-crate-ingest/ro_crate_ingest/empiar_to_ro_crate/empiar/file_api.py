from fs.ftpfs import FTPFS
from pydantic import BaseModel


import pathlib

from ro_crate_ingest.settings import get_settings


class EMPIARFile(BaseModel, frozen=True):
    path: pathlib.Path
    size_in_bytes: int


def get_files(accession_id: str) -> list[EMPIARFile]:
    # Note this is a dictionary to include reasons why the override was made
    overrides = {
        "EMPAIR-TEST": "A test submission.",
        "EMPIAR-ANNOTATIONTEST": "A test submission.",
    }
    if accession_id in overrides:
        return get_file_info_from_override(accession_id)
    else:
        return get_files_from_ftp(accession_id)


def get_file_info_from_override(accession_id: str) -> list[EMPIARFile]:
    override_dir = pathlib.Path(get_settings().empiar_override_dir, accession_id)
    data_path = override_dir / "data"
    return [
        EMPIARFile(
            path=str(pathlib.Path(file).relative_to(override_dir)),
            size_in_bytes=file.stat().st_size,
        )
        for file in data_path.rglob("*")
        if file.is_file()
    ]


def get_files_from_ftp(accession_id: str) -> list[EMPIARFile]:

    accession_no = accession_id.split("-")[1]
    ftp_fs = FTPFS("ftp.ebi.ac.uk")
    root_path = f"/empiar/world_availability/{accession_no}/data"
    walker = ftp_fs.walk(root_path)

    empiar_files = []

    for path, dirs, files in walker:
        for file in files:
            relpath = pathlib.Path(path).relative_to(root_path)
            empiar_file = EMPIARFile(path=relpath / file.name, size_in_bytes=file.size)
            empiar_files.append(empiar_file)

    return empiar_files
