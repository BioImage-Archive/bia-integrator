from typing import Optional
from rdflib import URIRef


class ContextTerm:
    full_uri: URIRef
    field_name: str
    type_mapping: Optional[str]

    def __init__(
        self,
        full_uri: str | URIRef,
        field_name: str,
        type_mapping: Optional[str] = None,
    ):
        self.full_uri = URIRef(full_uri)
        self.field_name = field_name
        self.type_mapping = type_mapping

    def to_context_term_dict(self, prefixes: Optional[dict[str, str]] = None) -> dict:
        context_term = {}

        id = self.full_uri

        if prefixes:
            # TODO: handle trailing / or # sensibly to reconstruct the correct term uri when using the context
            for prefix_name, prefix_uri in prefixes.items():
                if self.full_uri.startswith(prefix_uri):
                    # defaults to most specific prefix if there is more than one prefix that matches the uri
                    compact_id = (
                        f"{prefix_name}:{self.full_uri.removeprefix(prefix_uri)}"
                    )
                    if len(compact_id) < len(id):
                        id = compact_id

        context_term |= {"@id": id}

        if self.type_mapping:
            context_term |= {"@type": self.type_mapping}
        return context_term

    def to_mapping_dict(
        self, prefixes: Optional[dict[str, str]] = None
    ) -> dict[str, dict]:
        context_term = self.to_context_term_dict(prefixes)

        return {self.field_name: context_term}
