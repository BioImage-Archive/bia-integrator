import typer
import logging
from typing import Annotated, Optional
from pathlib import Path
from rich.logging import RichHandler
from ro_crate_ingest.save_utils import PersistenceMode
from ro_crate_ingest.ro_crate_to_api.api_conversion import convert_ro_crate_to_bia_api
from ro_crate_ingest.biostudies_to_ro_crate.biostudies_conversion import (
    convert_biostudies_to_ro_crate,
)

ro_crate_ingest = typer.Typer()

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()


@ro_crate_ingest.command("ingest")
def ro_crate_to_bia(
    crate_path: Annotated[
        Optional[Path],
        typer.Option(
            "--crate-path",
            "-c",
            case_sensitive=False,
            help="Path to the ro-crate root (or ro-crate-metadata.json)",
        ),
    ] = None,
    persistence_mode: Annotated[
        Optional[PersistenceMode],
        typer.Option(
            "--persistence-mode",
            "-p",
            case_sensitive=False,
            help="Mode to persist the data. Options: local_file, local_api, bia_api",
        ),
    ] = PersistenceMode.LOCAL_FILE,
):
    crate_path = crate_path.resolve()
    if crate_path.name == "ro-crate-metadata.json":
        crate_path = crate_path.parent

    convert_ro_crate_to_bia_api(crate_path, persistence_mode)


@ro_crate_ingest.command("biostudies-to-roc")
def biostudies_to_ro_crate(
    accession_id: Annotated[
        str,
        typer.Argument(
            help="Acccession id (e.g. S-BIADXXXX or S-BSSTXXXX) of the submission"
        ),
    ],
    crate_path: Annotated[
        Optional[Path],
        typer.Option(
            "--crate-path",
            "-c",
            case_sensitive=False,
            help="Path to output the ro-crate document",
        ),
    ] = None,
):

    convert_biostudies_to_ro_crate(accession_id, crate_path)
