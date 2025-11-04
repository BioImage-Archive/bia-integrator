from typing import Optional
from rdflib import URIRef


class FieldContext:

    uri: URIRef
    is_id_field: bool
    is_reverse_field: bool

    def __init__(self, uri: str, is_id_field: bool = False, is_reverse_field=False):
        self.uri = URIRef(uri)
        self.is_id_field = is_id_field
        self.is_reverse_field = is_reverse_field
