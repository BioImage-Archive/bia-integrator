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
from ro_crate_ingest.empiar_to_ro_crate.empiar_proposal_conversion import (
    convert_empiar_proposal_to_ro_crate,
)
from ro_crate_ingest.empiar_to_ro_crate.empiar_proposal_generation import (
    generate_empiar_proposal,
)
from ro_crate_ingest.minimal_ro_crate.minimal_ro_crate_creation import (
    make_minimal_ro_crate,
)
from ro_crate_ingest.ro_crate_modification.modifier import (
    apply_modifications
)
from ro_crate_ingest.validator.validation import bia_roc_validation

ro_crate_ingest = typer.Typer()

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()


@ro_crate_ingest.callback()
def main(
    verbose: Annotated[
        bool, typer.Option("--verbose", "-v", help="Enable debug logging.")
    ] = False,
):
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)


@ro_crate_ingest.command("ingest")
def ro_crate_to_bia(
    crate_path: Annotated[
        Path,
        typer.Option(
            "--crate-path",
            "-c",
            case_sensitive=False,
            help="Path to the ro-crate root (or ro-crate-metadata.json)",
        ),
    ],
    persistence_mode: Annotated[
        PersistenceMode,
        typer.Option(
            "--persistence-mode",
            "-p",
            case_sensitive=False,
            help="Mode to persist the data. Options: local_file, local_api, bia_api",
        ),
    ] = PersistenceMode.LOCAL_FILE,
    file_ref_url_prefix: Annotated[
        str | None,
        typer.Option(
            "--url-prefix",
            "-u",
            case_sensitive=False,
            help="File url prefix for file reference creation.",
        ),
    ] = None,
):
    crate_path = crate_path.resolve()
    if crate_path.name == "ro-crate-metadata.json":
        crate_path = crate_path.parent

    convert_ro_crate_to_bia_api(crate_path, persistence_mode, file_ref_url_prefix)


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
    fail_on_unprocessed_sections: Annotated[
        bool,
        typer.Option(
            "--fail-on-unprocessed-sections",
            help="Raise an error if there are non-empty sections that cannot be processed",
        ),
    ] = False,
):
    convert_biostudies_to_ro_crate(
        accession_id, crate_path, fail_on_unprocessed_sections
    )


@ro_crate_ingest.command("generate-empiar-proposal")
def empiar_proposal(
    proposal_config_path: Annotated[
        Path, typer.Argument(help="Path to the yaml proposal config file.")
    ],
    proposal_output_dir_path: Annotated[
        Optional[Path],
        typer.Option(
            "--proposal-dir-path",
            "-p",
            case_sensitive=False,
            help="Path to output proposal directory.",
        ),
    ] = None,
):
    generate_empiar_proposal(proposal_config_path, proposal_output_dir_path)


@ro_crate_ingest.command("empiar-to-roc")
def empiar_to_ro_crate(
    proposal_path: Annotated[
        Path,
        typer.Argument(help="Path to the yaml proposal file."),
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
    convert_empiar_proposal_to_ro_crate(proposal_path, crate_path)


@ro_crate_ingest.command("minimal-roc")
def minimal_ro_crate(
    accession_id: Annotated[
        str,
        typer.Argument(
            help="Acccession id (e.g. S-BIADXXXX, S-BSSTXXXX, or EMPIAR-XXXXX) of the submission"
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
    make_minimal_ro_crate(accession_id, crate_path)


@ro_crate_ingest.command("modify-roc")
def modify_ro_crate(
    ro_crate_path: Annotated[
        Path, 
        typer.Argument(
            case_sensitive=False, 
            help="Path to the ro-crate root (or ro-crate-metadata.json) to modify."
        )
    ],
    modification_config_path: Annotated[
        Path,
        typer.Argument(
            case_sensitive=False,
            help="Path to the yaml modification config file.",
        )
    ]
):
    apply_modifications(ro_crate_path, modification_config_path)


@ro_crate_ingest.command("validate")
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
