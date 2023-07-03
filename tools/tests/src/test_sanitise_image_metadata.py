import pytest
import json


from scripts.extract_ome_metadata import sanitise_image_metadata

dict_no_nesting = {
    "key1": "value1",
    "key2": None,
    "key2_unit": "nm",
    "key3": "null",
    "key3_unit": "mm",
    "key4": "value4",
    "key4_unit": "m",
    "key5": None,
    "key6": [],
    "key6_unit": "km",
}

sanitised_dict_no_nesting_expected_output = {
    "key1": "value1",
    "key4": "value4",
    "key4_unit": "m",
}

dict_with_nesting = {
    "key1": "value1",
    "key2": None,
    "key2_unit": "nm",
    "key3": {
        "nested_key3_1": "nested_key3_1_value",
        "nested_key3_1_unit": "m",
        "nested_key3_2": None,
        "nested_key3_2_unit": "km",
        "nested_key3_3": "null",
        "nested_key3_4": "nested_key3_4_value",
        "nested_key3_5": [
            dict_no_nesting,
            {
                "nested_key3_5_1": None,
                "nested_key3_5_1_unit": "m",
            },
        ],
    },
    "key3_unit": "mm",
    "key4": "value4",
    "key4_unit": "m",
    "key5": "null",
    "key6": [],
    "key6_unit": "km",
}

sanitised_dict_with_nesting_expected_output = {
    "key1": "value1",
    "key3": {
        "nested_key3_1": "nested_key3_1_value",
        "nested_key3_1_unit": "m",
        "nested_key3_4": "nested_key3_4_value",
        "nested_key3_5": [
            sanitised_dict_no_nesting_expected_output,
        ],
    },
    "key3_unit": "mm",
    "key4": "value4",
    "key4_unit": "m",
}

def test_sanitise_image_metadata():
    """Test function to sanitise image metadata"""
    
    sanitised_dict_no_nesting = sanitise_image_metadata(dict_no_nesting)
    assert sanitised_dict_no_nesting == sanitised_dict_no_nesting_expected_output

    sanitised_dict_with_nesting = sanitise_image_metadata(dict_with_nesting)
    assert sanitised_dict_with_nesting == sanitised_dict_with_nesting_expected_output
