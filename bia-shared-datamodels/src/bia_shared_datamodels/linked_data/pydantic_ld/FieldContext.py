from typing import Optional
from rdflib import URIRef


class FieldContext:

    uri: URIRef
    isIdField: bool

    def __init__(self, uri: str, isIdField: bool = False):
        self.uri = URIRef(uri)
        self.isIdField = isIdField
