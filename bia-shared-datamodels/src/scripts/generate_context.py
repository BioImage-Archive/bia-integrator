import json
from pathlib import Path
from bia_shared_datamodels.ro_crate_generator_utils import generate_standard_bia_context


def generate_bia_ro_crate_context(file_path: Path):

    context = generate_standard_bia_context()

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
