import json
from collections import defaultdict
from typing import Iterable

from bia_shared_datamodels.linked_data.ld_context.SimpleJSONLDContext import (
    SimpleJSONLDContext,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from rdflib import Graph
from pathlib import Path


class BIAROCrateMetadata:

    _graph_bia_entities: dict[str, ROCrateModel]
    _context: SimpleJSONLDContext
    _base_path: Path

    def __init__(
        self,
        graph_bia_entities: dict[str, ROCrateModel],
        context: SimpleJSONLDContext,
        base_path: Path,
    ) -> None:
        self._graph_bia_entities = graph_bia_entities
        self._context = context
        self._base_path = base_path

    def to_graph(self) -> Graph:
        graph = Graph()

        for entity in self._graph_bia_entities.values():
            graph += entity.to_graph(self._context, self._base_path)

        return graph

    def to_dict(self) -> dict:
        context_dict = self._context.to_dict()

        graph_objects = [
            json.loads(entity.model_dump_json(by_alias=True))
            for entity in sorted(
                self._graph_bia_entities.values(), key=lambda entity: entity.id
            )
        ]

        return {"@context": context_dict, "@graph": graph_objects}

    def get_context(self) -> SimpleJSONLDContext:
        return self._context

    def get_objects(self) -> Iterable[ROCrateModel]:
        return self._graph_bia_entities.values()

    def get_object_lookup(self) -> dict[str, ROCrateModel]:
        return self._graph_bia_entities

    def get_object(self, id: str) -> ROCrateModel | None:
        return self._graph_bia_entities.get(id)

    def get_objects_by_type(
        self,
    ) -> dict[type, dict[str, ROCrateModel]]:
        """
        Returns a dictionary of the form:
        {
            "type_A": {
                "id_a": <Object of type: type_A with id: id_a>
            }
        }
        """
        objects_by_type = defaultdict(dict)
        for object_id, bia_object in self._graph_bia_entities.items():
            objects_by_type[type(bia_object)][object_id] = bia_object

        return objects_by_type
