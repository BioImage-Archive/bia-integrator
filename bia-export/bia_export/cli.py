import typer
import logging
from rich.logging import RichHandler
from typing_extensions import Annotated
from pathlib import Path
from .website_conversion import create_studies
from typing import List
import json

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()

app = typer.Typer()


@app.command()
def website_study(
    accession_id_list: Annotated[List[str], typer.Argument(help="Accession IDs of the studies to export")],
    root_directory: Annotated[Path, typer.Option("--root", "-r", help="If root directory specified then use files there, rather than calling API")] = None,
    output_filename: Annotated[Path, typer.Option("--out_file", "-o",)] = Path("bia-images-export.json")
    ):

    abs_root = root_directory.resolve()
    studies_map = create_studies(accession_id_list, abs_root)

    logging.info(f"Writing study info to {output_filename.absolute()}")
    with open(output_filename, "w") as output:
        output.write(json.dumps(studies_map, indent=4))


@app.command()
def website_image():
    pass

if __name__ == "__main__":
    app()