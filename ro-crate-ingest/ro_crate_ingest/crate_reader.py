import json
import os
from pathlib import Path
import urllib.parse
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from rocrate.rocrate import ROCrate
import bia_shared_datamodels.ro_crate_models as ro_crate_models
import inspect
import pyld
import rdflib
import logging
import urllib
import requests

logger = logging.getLogger("__main__." + __name__)


def load_ro_crate_metadata_to_dict(crate_path: str) -> dict:
    crate_path: Path = Path(crate_path)

    if crate_path.is_dir():
        crate_metadata_path = crate_path / "ro-crate-metadata.json"
    else:
        crate_metadata_path = crate_path

    if not os.path.exists(crate_metadata_path):
        raise FileNotFoundError(f"File {crate_metadata_path} not found.")

    with open(crate_metadata_path, "r") as file:
        data = json.load(file)

    return data


def validate_json(data):
    # TODO: Implement actual validation logic using models & context. RO-CRATE json structure is still under a lot of discussion, so defaulting to True for now.
    return True


def load_entities(data: dict) -> dict[str, ROCrateModel]:
    # TODO: maybe loading using ro-crate libaries would be better
    context = data.get("@context", {})

    loaded_context = {}
    for item in context:
        if isinstance(item, str) and urllib.parse.urlparse(item):
            loaded_context |= load_external_context(item).get("@context", {})
        elif isinstance(item, dict):
            loaded_context |= item

    entities = data.get("@graph", [])
    crate_objects_by_id = {}
    classes = inspect.getmembers(
        ro_crate_models,
        lambda member: inspect.isclass(member)
        and member.__module__ == "bia_shared_datamodels.ro_crate_models"
        and issubclass(member, ROCrateModel),
    )

    for entity in entities:
        start_len = len(crate_objects_by_id)
        entity_type = expand_entity(entity, loaded_context).get("@type")
        for name, model in classes:
            if model.model_config["model_type"] in entity_type:
                object: ROCrateModel = model(**entity)
                if object.id in crate_objects_by_id.keys():
                    raise RuntimeError(
                        f"Duplicate object found in ro-crate with id: {object.id}"
                    )
                crate_objects_by_id[object.id] = object
                break
        if len(crate_objects_by_id) == start_len:
            if "ro-crate-metadata.json" == entity.get("@id"):
                logger.info("Skipping ro-crate-metadata.json entity.")
            elif str(rdflib.RDF.Property) in entity_type:
                logger.info(
                    f"Skipping RDF.Property: {entity.get('name')}. Though we may want to processes these in some way later"
                )
            else:
                logger.warning(
                    f"Could not find class for entity of types: {entity_type}"
                )
                logger.debug(f"Entity: {entity}")
    return crate_objects_by_id


def crate_read(path: Path):
    crate = ROCrate(path)
    return crate


def process_ro_crate(crate_path):
    data = load_ro_crate_metadata_to_dict(crate_path)
    if validate_json(data):
        return load_entities(data)
    else:
        print("Invalid JSON data.")
        return []


def map_files_to_datasets(crate_path: str, datasets: list):
    crate_path = Path(crate_path)
    files = []

    for root, _, filenames in os.walk(crate_path):
        for filename in filenames:
            file_path = Path(root) / filename
            files.append(file_path)

    file_mapping = {}
    for file in files:
        for dataset in datasets:
            if dataset.id in str(file):
                if dataset.id not in file_mapping:
                    file_mapping[dataset.id] = []
                file_mapping[dataset.id].append(file)

    return file_mapping


def expand_entity(entity: dict, context: dict) -> str:
    document = {"@context": context, "@graph": [entity]}
    expanded = pyld.jsonld.expand(document)
    assert len(expanded) == 1
    return expanded[0]


def load_external_context(url) -> dict:
    """
    Load an external context from a URL.
    """
    try:
        context = requests.get(url).json()
        return context
    except Exception as e:
        logger.error(f"Failed to load context from {url}: {e}")
        return {}


def load_ro_crate_metadata_to_graph(crate_path: str) -> rdflib.Graph:
    crate_path: Path = Path(crate_path)

    if crate_path.is_dir():
        crate_metadata_path = crate_path / "ro-crate-metadata.json"
    else:
        crate_metadata_path = crate_path

    if not os.path.exists(crate_metadata_path):
        raise FileNotFoundError(f"File {crate_metadata_path} not found.")

    graph = rdflib.Graph()

    graph.parse(crate_metadata_path, format="json-ld")

    return graph
