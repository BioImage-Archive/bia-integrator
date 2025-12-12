from ro_crate_ingest.bia_ro_crate.parser.jsonld_metadata_parser import (
    JSONLDMetadataParser,
)
from rdflib import Graph
from pathlib import Path
import pytest_check as check


def test_parser_to_graph_equivalent():
    ro_crate = (
        Path(__file__).parent
        / "ro_crate_to_bia"
        / "input_ro_crate"
        / "S-TEST_overlapping_file_list_and_ro_crate_info"
    )

    parser = JSONLDMetadataParser()
    parser.parse(ro_crate)
    metadata = parser.result
    metadata_graph = metadata.to_graph()

    direct_graph = Graph()
    direct_graph.parse(
        ro_crate / "ro-crate-metadata.json",
        format="json-ld",
    )

    assert len(metadata_graph) == len(direct_graph)
    for statement in metadata_graph:
        direct_statement = list(direct_graph.triples(statement))
        check.equal(len(direct_statement), 1)
