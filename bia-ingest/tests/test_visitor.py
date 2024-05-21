from bia_ingest.visitor import Visitor


def test_visitor(accession_id, submission_from_json):
    visitor = Visitor(accession_id)
    visitor.visit("root", submission_from_json)
    assert visitor.result is not None
