"""Compare contents in submission in biostudies with that in BIA API

"""

import typer
import json
from pathlib import Path
from logging import Logger
from typing import Any

import requests
from bia_ingest.scli import rw_client
from bia_ingest.visitor import Visitor

logger = Logger("")


def compare_biostudies_with_api(
    from_biostudies: dict[str, Any], from_api: dict[str, Any]
) -> dict[str, list[str]]:
    """Return dict showing values mapped successfully and those not mapped

    Args:
        from_biostudes (dict[str, Any]): dict returned by 
            Visitor.flattened_contents_dict after visiting all nodes in a 
            biostudies Submission
        from_api (dict[str, Any]): dict returned by 
            Visitor.flattened_contents_dict after visiting all nodes in a
            BIA API Study object augmented with Images and File references

    Returns:
        dict[str, list[str]]: dict containing two keys 
            "mapped" -> list of dotted paths mapped from biostudies to api
            "not_mapped" -> list of dotted paths in biostudies not in api.
    """

    result = {
        "mapped": [],
        "not_mapped": [],
    }

    from_api_values = list(from_api.values())
    from_api_keys = list(from_api.keys())

    for key, value in from_biostudies.items():
        if key.endswith(".name"):
            last_name = key
            last_value = value
            continue
        elif key.endswith(".value"):
            if last_name.strip(".name") == key.strip(".value"):
                key = f"{last_name}={last_value}"
        try:
            index = from_api_values.index(value)
            result["mapped"].append(f"From API {from_api_keys[index]} mapped to {key}")
        except ValueError:
            result["not_mapped"].append(key)

    return result


app = typer.Typer()


@app.command()
def main(accession_id: str, output_path: str = "") -> None:

    url = f"https://www.ebi.ac.uk/biostudies/files/{accession_id}/{accession_id}.json"
    from_biostudies = requests.get(url).json()
    visitor = Visitor(accession_id)
    visitor.visit("", from_biostudies)
    from_biostudies = visitor.flattened_contents_dict

    # If study not in API use an empty dict
    # Catch IndexError as load_and_annotate_study throws this if
    # accession_id not found
    study_info = rw_client.get_object_info_by_accession([accession_id,])
    n_studies = len(study_info)
    if n_studies == 0:
        from_api = {}
    elif n_studies == 1:
        study = rw_client.get_study(study_info[0].uuid)
        study_dict = study.dict()
        study_dict["file_references"] = [
            fileref.dict for fileref in rw_client.get_study_file_references(study.uuid)
        ]
        study_dict["images"] = [
            image.dict for image in rw_client.get_study_images(study.uuid)
        ]
        visitor.reset(accession_id)
        visitor.visit("", study_dict)
        from_api = visitor.flattened_contents_dict
    else:
        raise Exception(
            f"Got more than one value querying info for {accession_id}. Return value: {study_info}"
        )

    comparison_result = compare_biostudies_with_api(from_biostudies, from_api)

    if output_path == "":
        output_path = Path.cwd() / f"{accession_id}-comparison-result.json"
    Path(output_path).write_text(json.dumps(comparison_result, indent=2))
    logger.info(f"Written comparison result to {output_path}")


if __name__ == "__main__":
    app()
