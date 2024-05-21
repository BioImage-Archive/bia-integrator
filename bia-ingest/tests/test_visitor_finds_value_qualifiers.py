from bia_ingest.visitor import Visitor

submission = {
    "accno": "S-BIAD0001",
    "title": "Test Submission",
    "attributes": [
        {
            "name": "test_attribute_name",
            "value": "test_attribute_value",
            "valqual": [
                {
                    "name": "test_value_qualifier_name_1",
                    "value": "test_value_qualifier_value_1",
                },
                {
                    "name": "test_value_qualifier_name_2",
                    "value": "test_value_qualifier_value_2",
                },
                {
                    "name": "test_value_qualifier_name_3",
                    "value": "test_value_qualifier_value_3",
                },
            ],
        },
        {"name": "ReleaseDate", "value": "2024-02-21"},
        {"name": "AttachTo", "value": "BioImages"},
    ],
    "type": "submission",
}

expected_result = [
    "test_attribute_value",
    {"test_value_qualifier_name_1": "test_value_qualifier_value_1",},
    {"test_value_qualifier_name_2": "test_value_qualifier_value_2",},
    {"test_value_qualifier_name_3": "test_value_qualifier_value_3",},
]


def test_find_value_qualifiers():
    visitor = Visitor("dummy_accession_id")
    visitor.visit("root", submission)
    assert visitor.result["study"][0]["test_attribute_name"] == expected_result
