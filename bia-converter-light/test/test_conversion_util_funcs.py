from bia_converter_light import utils


def test_merge_dicts():
    dict_list = [
        {"key1": "value1", "key2": "value2"},
        {"key1": "value3", "key4": "value4"},
    ]

    assert utils.merge_dicts(dict_list) == {
        "key1": ["value1", "value3"],
        "key2": "value2",
        "key4": "value4",
    }
