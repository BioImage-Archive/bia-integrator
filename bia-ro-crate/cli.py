import logging
from pathlib import Path
from typing import Annotated

import typer
from rich.logging import RichHandler

from validator.validation import bia_roc_validation

bia_ro_crate = typer.Typer()

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()


@bia_ro_crate.callback()
def main(
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable debug logging.")
    ] = False,
):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@bia_ro_crate.command("validate")
def validate_ro_crate(
    crate_path: Annotated[
        Path,
        typer.Argument(
            case_sensitive=False,
            help="Path to the ro-crate root (or ro-crate-metadata.json)",
        ),
    ],
):
    bia_roc_validation(crate_path)
