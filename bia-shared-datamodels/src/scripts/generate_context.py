from bia_shared_datamodels.linked_data.ld_context.SimpleJSONLDContext import (
    SimpleJSONLDContext,
)
import bia_shared_datamodels.ro_crate_models as ro_crate_models
import json
import inspect
from pathlib import Path
import bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel as ROCrateModel


def generate_bia_ro_crate_context(file_path: Path):

    prefixes = {
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "schema": "http://schema.org/",
        "dc": "http://purl.org/dc/terms/",
        "bia": "http://bia/",
        "csvw": "http://www.w3.org/ns/csvw#",
    }

    context = SimpleJSONLDContext(prefixes=prefixes)

    ro_crate_pydantic_models = inspect.getmembers(
        ro_crate_models,
        lambda member: inspect.isclass(member)
        and member.__module__ == "bia_shared_datamodels.ro_crate_models"
        and issubclass(member, ROCrateModel.ROCrateModel),
    )

    for name, ldclass in ro_crate_pydantic_models:
        for field_term in ldclass.generate_field_context():
            context.add_term(field_term)

    with open(file_path, "w") as f:
        json.dump({"@context": context.to_dict()}, f, indent=2)


if __name__ == "__main__":
    path_to_context = (
        Path(__file__).parents[1]
        / "bia_shared_datamodels"
        / "linked_data"
        / "bia_ro_crate_context.jsonld"
    )
    generate_bia_ro_crate_context(path_to_context)
    print(f"BIA RO-Crate context generated at: {path_to_context}")
