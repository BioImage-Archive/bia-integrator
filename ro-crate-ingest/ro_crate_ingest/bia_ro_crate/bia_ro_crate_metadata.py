import json
from typing import Iterable

from bia_shared_datamodels.linked_data.ld_context.SimpleJSONLDContext import (
    SimpleJSONLDContext,
)
from bia_shared_datamodels.linked_data.pydantic_ld.ROCrateModel import ROCrateModel
from rdflib import Graph
from rocrate import rocrate


class BIAROCrateMetadata(rocrate.ROCrate):

    graph_bia_entities: dict[str, ROCrateModel]
    context: SimpleJSONLDContext

    def __init__(
        self,
        graph_bia_entities: dict[str, ROCrateModel],
        context: SimpleJSONLDContext,
    ) -> None:
        self.graph_bia_entities = graph_bia_entities
        self.context = context

    def to_graph(self) -> Graph:
        graph = Graph()
        return graph

    def to_dict(self) -> dict:
        context_dict = self.context.to_dict()

        graph_objects = [
            json.loads(entity.model_dump_json(by_alias=True))
            for entity in sorted(
                self.graph_bia_entities.values(), key=lambda entity: entity.id
            )
        ]

        return {"@context": context_dict, "@graph": graph_objects}

    def objects(self) -> Iterable[ROCrateModel]:
        return self.graph_bia_entities.values()

    def get_object(self, id) -> ROCrateModel | None:
        return self.graph_bia_entities.get(id)

    def get_objects_by_type(self, filter_type: type) -> dict[str, ROCrateModel]:
        return {
            object_id: bia_object
            for object_id, bia_object in self.graph_bia_entities.items()
            if isinstance(bia_object, filter_type)
        }
