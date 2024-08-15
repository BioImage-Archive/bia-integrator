import typer
import logging
import json
from rich.logging import RichHandler
from typing_extensions import Annotated
from pathlib import Path
from .website_conversion import create_study, create_ec_images

logging.basicConfig(
    level="NOTSET", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger()

app = typer.Typer()


@app.command()
def website_study(
    accession_id: Annotated[
        str, typer.Argument(help="Accession ID of the study to export")
    ],
    root_directory: Annotated[
        Path,
        typer.Option(
            "--root",
            "-r",
            help="If root directory specified then use files there, rather than calling API",
        ),
    ] = None,
    output_filename: Annotated[
        Path,
        typer.Option(
            "--out_file",
            "-o",
        ),
    ] = Path("bia-export.json"),
):

    if root_directory:
        abs_root = root_directory.resolve()
    study = create_study(accession_id, abs_root)

    logging.info(f"Writing study info to {output_filename.absolute()}")
    with open(output_filename, "w") as output:
        output.write(study.model_dump_json(indent=4))


@app.command()
def website_image(
    accession_id: Annotated[
        str, typer.Argument(help="Accession ID of the study to export")
    ],
    root_directory: Annotated[
        Path,
        typer.Option(
            "--root",
            "-r",
            help="If root directory specified then use files there, rather than calling API",
        ),
    ] = None,
    output_filename: Annotated[
        Path,
        typer.Option(
            "--out_file",
            "-o",
        ),
    ] = Path("bia-image-export.json"),
):

    if root_directory:
        abs_root = root_directory.resolve()
    image_map = create_ec_images(accession_id, abs_root)

    logging.info(f"Writing website images to {output_filename.absolute()}")
    with open(output_filename, "w") as output:
        output.write(json.dumps(image_map, indent=4))


if __name__ == "__main__":
    app()
