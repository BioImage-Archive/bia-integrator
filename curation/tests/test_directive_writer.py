from curation.writer.yaml_directive_writer import YamlDirectiveWriter
from curation.directive.attribute_directive import AttributeDirective
from curation.parser.yaml_directive_parser import YamlDirectivePaser
import pytest
from uuid import uuid4
from copy import deepcopy


def test_update_written_directive(tmp_path):
    file_to_write_to = tmp_path / "diretive.yaml"

    directives = [
        AttributeDirective.model_validate(
            {
                "target_uuid": uuid4(),
                "object_type": "Study",
                "value": "test_value_1",
                "command": "update_attribute",
                "name": "test_attr",
            }
        ),
        AttributeDirective.model_validate(
            {
                "target_uuid": uuid4(),
                "object_type": "Study",
                "value": "test_value_2",
                "command": "update_attribute",
                "name": "test_attr",
            }
        ),
    ]

    writer = YamlDirectiveWriter()
    writer.write(file_to_write_to, directives)

    parser = YamlDirectivePaser()
    written_directives = parser.parse(file_to_write_to)

    assert written_directives == directives

    updated_directives = deepcopy(directives)
    updated_directives[0].value = "updated_test_value_1"

    writer.update(file_to_write_to, [updated_directives[0]])
    parser = YamlDirectivePaser()
    written_directives = parser.parse(file_to_write_to)
    assert written_directives != directives
    assert written_directives == updated_directives
