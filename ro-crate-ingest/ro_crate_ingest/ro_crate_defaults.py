import json
import os

from pydantic import BaseModel
from pathlib import Path
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels import ro_crate_generator_utils


def get_default_context():
    with open(
        Path(__file__).parents[2]
        / "bia-shared-datamodels"
        / "src"
        / "bia_shared_datamodels"
        / "linked_data"
        / "bia_ro_crate_context.jsonld"
    ) as f:
        bia_specific_context = json.loads(f.read())

    bia_ro_crate_context = [
        "https://w3id.org/ro/crate/1.1/context",
        bia_specific_context["@context"],
    ]

    return bia_ro_crate_context


def write_ro_crate_metadata(
    crate_path: Path, ro_crate_context: list | dict, graph: list[BaseModel]
):
    with open(crate_path / "ro-crate-metadata.json", "w") as f:
        f.write(
            json.dumps(
                {
                    "@context": ro_crate_context,
                    "@graph": [
                        json.loads(x.model_dump_json(by_alias=True))
                        for x in reversed(graph)
                    ],
                },
                indent=4,
            )
        )


def create_ro_crate_folder(accession_id: str, crate_path: Path | None = None) -> Path:
    output_path = crate_path if crate_path else Path(__file__).parents[1]
    ro_crate_dir = output_path / accession_id
    if not os.path.exists(ro_crate_dir):
        os.makedirs(ro_crate_dir)

    return ro_crate_dir


def get_all_ro_crate_classes() -> dict[str, type[ROCrateModel]]:
    return ro_crate_generator_utils.get_all_ro_crate_classes()
