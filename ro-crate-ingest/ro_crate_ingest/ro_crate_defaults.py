from pydantic import BaseModel, Field
from pathlib import Path
import json
from typing import Optional
import os
import bia_shared_datamodels.ro_crate_models as ROCrateModels
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
import inspect
from functools import lru_cache


class ROCrateCreativeWork(BaseModel):
    id: str = Field(alias="@id", default="ro-crate-metadata.json")
    type: str = Field(alias="@type", default="CreativeWork")
    conformsTo: dict = Field(default={"@id": "https://w3id.org/ro/crate/1.1"})
    about: dict = Field(default={"@id": "./"})


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


def create_ro_crate_folder(
    accession_id: str, crate_path: Optional[Path] = None
) -> Path:
    output_path = crate_path if crate_path else Path(__file__).parents[1]
    ro_crate_dir = output_path / accession_id
    if not os.path.exists(ro_crate_dir):
        os.makedirs(ro_crate_dir)

    return ro_crate_dir


@lru_cache
def get_all_ro_crate_classes() -> dict:
    ro_crate_pydantic_models = {
        ro_crate_class.model_config["model_type"]: ro_crate_class
        for name, ro_crate_class in inspect.getmembers(
            ROCrateModels,
            lambda member: inspect.isclass(member)
            and member.__module__ == "bia_shared_datamodels.ro_crate_models"
            and issubclass(member, ROCrateModel),
        )
    }
    return ro_crate_pydantic_models
