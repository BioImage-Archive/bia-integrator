from ro_crate_ingest.bia_ro_crate.parser.Parser import Parser
from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata
import json
from pathlib import Path
from typing import Iterable

import pyld
from bia_shared_datamodels.linked_data.ld_context import (
    ContextTerm,
    SimpleJSONLDContext,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from bia_shared_datamodels.ro_crate_generator_utils import get_all_ro_crate_classes
from rdflib import Graph

from ro_crate_ingest.bia_ro_crate.bia_ro_crate_metadata import BIAROCrateMetadata


class JSONLDParser(Parser[BIAROCrateMetadata]):

    def __init__(self, context=None) -> None:
        super().__init__(context)

    def parse(self, data):
        crate_metadata_path = self._get_metadata_path(path_to_ro_crate)
        if parser_classes:
            parser_classes_map: dict[str, type[ROCrateModel]] = {
                ro_crate_class.model_config["model_type"]: ro_crate_class
                for ro_crate_class in parser_classes
            }
        else:
            parser_classes_map = get_all_ro_crate_classes()

        with open(crate_metadata_path, "r") as jsonfile:
            json_dict = json.loads(jsonfile.read())

        context = self._resolve_context(json_dict["@context"])
        entities: list[dict] = json_dict["@graph"]

        rocrate_objects_by_id = {}
        for entity in entities:
            entity_type = self._expand_entity(entity, context.to_dict()).get(
                "@type", ()
            )
            for entity_type in entity_type:
                if entity_type in parser_classes_map:
                    model = parser_classes_map[entity_type]
                    object = model(**entity)
                    rocrate_objects_by_id[object.id] = object
                    break

        return BIAROCrateMetadata(
            graph_bia_entities=rocrate_objects_by_id,
            context=context,
        )

    def parse_to_graph(self, path_to_ro_crate: Path) -> Graph:
        """
        This function exists here until a BIAROCrateMetadata can create a graph of it's data - at which point that should probably be used instead.
        """
        crate_metadata_path = self._get_metadata_path(path_to_ro_crate)
        graph = Graph()
        graph.parse(crate_metadata_path, format="json-ld")
        return graph

    @staticmethod
    def _get_metadata_path(path: Path):
        if path.is_dir():
            crate_metadata_path = path / "ro-crate-metadata.json"
        else:
            crate_metadata_path = path
        return crate_metadata_path

    @staticmethod
    def _expand_entity(
        entity: dict, context: dict | list | str
    ) -> dict[str, str | list[dict] | list[str]]:
        document = {"@context": context, "@graph": [entity]}
        expanded = pyld.jsonld.expand(document)
        return expanded[0]

    @staticmethod
    def _resolve_context(
        context: dict | list | str,
    ) -> SimpleJSONLDContext.SimpleJSONLDContext:
        # Using pyld's JsonLdProcessor to handle the possible variablitiy in context definition structure
        jsonld_processor = pyld.jsonld.JsonLdProcessor()
        mappings = jsonld_processor.process_context(
            active_ctx={"mappings": {}}, local_ctx=context, options=None
        )["mappings"]

        terms = set()
        prefixes = {}
        for key, mapping in mappings.items():
            if mapping.get("_prefix"):
                prefixes[key] = mapping.get("@id")
            else:
                terms.add(
                    ContextTerm.ContextTerm(
                        full_uri=mapping.get("@id"),
                        field_name=key,
                        is_reverse=mapping.get("reverse"),
                    )
                )
        return SimpleJSONLDContext.SimpleJSONLDContext(prefixes=prefixes, terms=terms)
