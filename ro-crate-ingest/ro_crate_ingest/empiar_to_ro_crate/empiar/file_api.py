import pathlib
import aioftp
import asyncio
from pydantic import BaseModel
from ro_crate_ingest.settings import get_settings


class EMPIARFile(BaseModel, frozen=True):
    path: pathlib.Path
    size_in_bytes: int


def get_files(accession_id: str) -> list[EMPIARFile]:
    # Note this is a dictionary to include reasons why the override was made
    overrides = {
        "EMPIAR-IMAGEPATTERNTEST": "A test submission covering file pattern shapes.",
        "EMPIAR-STARFILETEST": "A test submission covering star file annotation, with tomograms, and other image dependencies.",
        "EMPIAR-IMAGELABELTEST": "A test submission covering file-to-image grouping strategies."
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
            path=pathlib.Path(file).relative_to(override_dir),
            size_in_bytes=file.stat().st_size,
        )
        for file in data_path.rglob("*")
        if file.is_file()
    ]


async def get_files_from_ftp_async(accession_id: str) -> list[EMPIARFile]:
    accession_no = accession_id.split("-")[1]
    root_path = pathlib.Path(f"/empiar/world_availability/{accession_no}")
    data_path = root_path / "data"

    empiar_files = []

    async with aioftp.Client.context("ftp.ebi.ac.uk") as client:
        try:
            async for path, path_info in client.list(data_path, recursive=True):
                if path_info["type"] == "file":
                    rel_path = path.relative_to(root_path)
                    empiar_files.append(
                        EMPIARFile(
                            path=rel_path, size_in_bytes=int(path_info.get("size", 0))
                        )
                    )
        except aioftp.StatusCodeError as e:
            # skip directories/files we can't access
            pass

    return empiar_files


def get_files_from_ftp(accession_id: str) -> list[EMPIARFile]:
    files = asyncio.run(get_files_from_ftp_async(accession_id))
    return files
