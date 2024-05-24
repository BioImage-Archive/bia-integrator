"""Load details from biostudies submission into API Biosample model

"""
from bia_ingest.visitor import Visitor


def test_read_biosample(accession_id, submission_from_json, expected_biosample):
    visitor = Visitor(accession_id)
    visitor.visit("root", submission_from_json)
    extracted_biosample = visitor.extracted_entities["biosample"][-1]

    assert extracted_biosample == expected_biosample
