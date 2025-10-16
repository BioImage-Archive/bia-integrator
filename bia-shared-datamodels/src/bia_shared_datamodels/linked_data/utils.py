import pathlib
import rdflib


def load_bia_ontology() -> rdflib.Graph:
    # TODO replace with URL once it's hosted somewhere properlly.
    turtle_ontology_path = pathlib.Path(__file__).parent / "bia_ontology.ttl"
    return rdflib.Graph().parse(turtle_ontology_path)
