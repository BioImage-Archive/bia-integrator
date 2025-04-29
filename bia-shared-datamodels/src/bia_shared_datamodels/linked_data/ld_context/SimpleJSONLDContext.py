from __future__ import annotations
from .ContextTerm import ContextTerm
from typing import Optional, Iterable


class SimpleJSONLDContext:
    prefixes: dict[str, str]
    terms: list[ContextTerm]

    def __init__(
        self,
        prefixes: Optional[dict[str, str]] = None,
        terms: Optional[list[ContextTerm]] = None,
    ):
        self.prefixes = prefixes if prefixes else {}
        self.terms = terms if terms else []

    def to_dict(self) -> dict:
        context_dict = self.prefixes.copy()

        for term in self.terms:
            context_dict |= term.to_mapping_dict(self.prefixes)

        return context_dict

    def add_prefix(self, short_term: str, uri: str) -> None:
        self.prefixes[short_term] = uri

    def remove_prefix(self, prefix) -> None:
        self.prefixes.pop(prefix)

    def add_term(self, term: ContextTerm) -> None:
        self.terms.append(term)

    def remove_field_term(self, field: str) -> None:
        self.terms = [term for term in self.terms if term.field_name != field]

    def merge(self, *contexts: Iterable[SimpleJSONLDContext]) -> SimpleJSONLDContext:
        """Merge multiple SimpleJSONLDContext instances into a new one."""
        merged_prefixes = self.prefixes.copy()
        merged_terms = self.terms.copy()

        context: SimpleJSONLDContext
        for context in contexts:
            for prefix, uri in context.prefixes.items():
                if prefix in merged_prefixes and merged_prefixes[prefix] != uri:
                    raise ValueError(f"Prefix conflict: {prefix} maps to multiple URIs")
                merged_prefixes[prefix] = uri

            existing_fields = {term.field_name for term in merged_terms}
            for term in context.terms:
                if term.field_name not in existing_fields:
                    merged_terms.append(term)

        return SimpleJSONLDContext(prefixes=merged_prefixes, terms=merged_terms)
