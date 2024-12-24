from pathlib import Path
import json
import typer
from typing_extensions import Annotated

import logging
from rich.logging import RichHandler

logging.basicConfig(
    level=logging.INFO, format="%(message)s", handlers=[RichHandler(show_time=False)]
)
logger = logging.getLogger()

app = typer.Typer(
    name="combine-export-files",
    help="Create specified representations",
)


@app.command(help="Combine the export files for accession ids specified in a manifest")
def combine_export_files(
    manifest_path: Annotated[str, typer.Argument()],
    verbose: Annotated[bool, typer.Option("-v")] = False,
) -> None:
    """Combine the export files for accession ids specified in a manifest

    Combine the export files individual studies into singles ones
    """

    if verbose:
        logger.setLevel(logging.DEBUG)

    accession_ids = [
        line.split(":")[-1]
        for line in Path(manifest_path).read_text().strip().split("\n")
    ]
    combined = {
        "bia-study-metadata": {},
        "bia-dataset-metadata": {},
        "bia-image-export": {},
    }
    input_base_path = Path(manifest_path).parent
    for accession_id in accession_ids:
        for metadata in combined.keys():
            input_path = input_base_path / f"{metadata}-{accession_id}.json"
            if input_path.is_file():
                metadata_in = json.loads(input_path.read_text())
                combined[metadata].update(metadata_in)
            else:
                if metadata == "bia-study-metadata":
                    # If no study metadata don't write anything
                    msg = f"No study metadata for {accession_id}. Not writing study, dataset or image metadata!"
                elif metadata == "bia-dataset-metadata":
                    # If no dataset OK. to write study, don't write Image
                    msg = f"No dataset metadata for {accession_id}. Study metadata written, but not writing dataset or image metadata!"
                else:
                    msg = f"No Image metadata for {accession_id}. Study and dataset metadata written, but not writing image metadata!"
                logger.warning(msg)
                break

    for metadata in combined.keys():
        input_path = input_base_path / f"{metadata}.json"
        if metadata == "bia-study-metadata":
            sorted_metadata = sorted(
                combined[metadata].items(),
                key=lambda x: x[1]["release_date"],
                reverse=True,
            )
            input_path.write_text(json.dumps(dict(sorted_metadata), indent=2))
        else:
            input_path.write_text(json.dumps(combined[metadata], indent=2))


@app.callback()
def main() -> None:
    return


if __name__ == "__main__":
    app()
