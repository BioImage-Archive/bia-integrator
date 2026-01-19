import yaml
from pathlib import Path
from typing import Iterable
from uuid import UUID

from bia_integrator_api.models import Provenance, ImageRepresentation
from curation.directive.attribute_directive import AttributeDirective, AttributeCommand
from curation.directive.base_directive import Directive
from curation.writer.yaml_directive_writer import YamlDirectiveWriter


def create_ng_link_directive(
    ng_view_link: str, 
    image_representation_uuid: UUID | str
) -> AttributeDirective:
    attribute_directive_dict = {
        "target_uuid": image_representation_uuid,
        "object_type": ImageRepresentation,
        "provenance": Provenance.BIA_CURATION,
        "command": AttributeCommand.UPDATE_ATTRIBUTE,
        "name": "neuroglancer_view_link",
        "value": ng_view_link,
        "attribute_model": None,
    }

    return AttributeDirective.model_validate(attribute_directive_dict)


def write_directives(
    directives: Iterable[Directive], 
    dry_run: bool
):
    if dry_run:
        print("\n" + "="*60)
        print("DRY RUN - Directives that would be written:")
        print("="*60 + "\n")
        
        directives_list = [d.model_dump(mode='json') for d in directives]
        print(yaml.dump(directives_list, default_flow_style=False, sort_keys=False))
        
        print("="*60)
        print("Not written, and DO NOT, write to file - ran in dry run mode")
        print("Use --output-mode s3 or both to write directives to curation")
        print("="*60 + "\n")
    else:
        output_path = (
            Path(__file__).parents[2]
            / "curation"
            / "directives"
            / "point_annotation_ng_view_links.yaml"
        )
        directive_writer = YamlDirectiveWriter()
        directive_writer.update(output_path, directives)
