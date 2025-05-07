from typer.testing import CliRunner
from bia_export.cli import (
    app,
)
import json

runner = CliRunner()


input_path = "/Users/fsherwood/workspace/BIA-astro/src/data/bia-study-metadata.json"

outpath = "/Users/fsherwood/workspace/bia-integrator/bia-export/bia-image-file-reference-mapping.json"

accession_ids = []

with open(input_path, "r") as f:
    json_result = json.load(f)
    for key in json_result.keys():
        accession_ids.append(key)


for accession_id in accession_ids:
    result = runner.invoke(
        app,
        [
            "image-uuid-mapping",
            "export",
            accession_id,
            "-u",
            outpath,
        ],
    )
    print(f"{accession_id}: {result.exit_code}")
