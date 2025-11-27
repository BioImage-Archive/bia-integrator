from uuid import UUID
from bia_integrator_api.models import Provenance, ImageRepresentation
from curation.directive.attribute_directive import AttributeDirective, AttributeCommand
from curation.directive.base_directive import Directive
from curation.writer.yaml_directive_writer import YamlDirectiveWriter
from typing import Iterable
from pathlib import Path


def create_ng_link_directive(
    s3_url: str, image_representation_uuid: UUID | str
) -> AttributeDirective:
    attribute_directive_dict = {
        "target_uuid": image_representation_uuid,
        "object_type": ImageRepresentation,
        "provenance": Provenance.BIA_CURATION,
        "command": AttributeCommand.UPDATE_ATTRIBUTE,
        "name": "neuroglancer_view_link",
        "value": s3_url,
        "attribute_model": None,
    }

    return AttributeDirective.model_validate(attribute_directive_dict)


def write_directives(directives: Iterable[Directive]):
    path = (
        Path(__file__).parents[2]
        / "curation"
        / "directives"
        / "point_annotation_ng_view_links.yaml"
    )

    directive_writer = YamlDirectiveWriter()
    directive_writer.update(path, directives)
