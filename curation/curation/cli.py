import logging
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer
from rich.logging import RichHandler

from curation.bia_api_client import BIAAPIClient
from curation.curator.object_attribute_curator import ObjectAttributeCurator
from curation.curator.object_field_curator import ObjectFieldCurator
from curation.directive.attribute_directive import AttributeDirective
from curation.directive.field_directive import FieldDirective
from curation.parser.yaml_directive_parser import YamlDirectivePaser
from curation.settings import get_settings

logging.basicConfig(
    level="WARNING", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()]
)
logger = logging.getLogger(__name__)
logger.setLevel("INFO")

curate = typer.Typer()


class APIMode(str, Enum):
    LOCAL = "local"
    DEV = "dev"


@curate.command()
def apply_directive(
    directive_file_path: Annotated[
        Path,
        typer.Argument(help="Path to diretive."),
    ],
    api_mode: Annotated[
        APIMode,
        typer.Option(
            help="Whether to modify objects on a locally running copy of the api, or some other (e.g. dev)."
        ),
    ] = APIMode.LOCAL,
):
    settings = get_settings()

    if api_mode == APIMode.DEV:
        settings.configure_for_dev_api()

    api_client = BIAAPIClient(settings=settings)

    directive_parser = YamlDirectivePaser()
    directives = directive_parser.parse(directive_file_path)

    logger.info(f"Parsed {len(directives)} directives.")

    field_curator = ObjectFieldCurator()
    attribute_curator = ObjectAttributeCurator()

    modified_api_objects = {}

    for directive in directives:
        api_object = modified_api_objects.get(directive.target_uuid)
        if not api_object:
            api_object = api_client.get_object_by_type(
                directive.target_uuid, directive.object_type
            )

        match directive:
            case FieldDirective():
                updated_api_object = field_curator.update(api_object, directive)
            case AttributeDirective():
                updated_api_object = attribute_curator.update(api_object, directive)
            case _:
                raise RuntimeError(f"Unhandled directive type: {type(directive)}")

        modified_api_objects[updated_api_object.uuid] = updated_api_object

    logger.info(f"Created {len(modified_api_objects)} modified API objects.")

    for modified_object in modified_api_objects.values():
        api_client.update_existing_object(modified_object)
