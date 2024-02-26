import logging
from pathlib import Path
from bia_integrator_api import models as api_models
from typing import Optional, List
from uuid import UUID
import time
from typing_extensions import Annotated
from enum import Enum
from pydantic import BaseModel
from rich import print
import json

logger = logging.getLogger("biaint")
logging.basicConfig(level=logging.INFO)

import typer

from bia_integrator_core.interface import (
    get_study,
    get_all_studies,
    get_image_by_alias,
    get_image,
    get_images,
    get_filerefs,
    get_study_annotations,
    persist_study_annotation,
    persist_image_representation,
    get_representations,
    persist_image_annotation,
    persist_collection,
    update_collection,
    get_collections,
    get_study_tags,
    add_study_tag,
    get_collection,
    persist_image_alias,
    to_uuid,
    get_bia_user,
    study_recount
)
from bia_integrator_core.integrator import load_and_annotate_study

class OutputFormat(str, Enum):
    PRETTY = "pretty"
    JSON = "json"

    @staticmethod
    def fields_project(field_names: List[str], source: BaseModel):
        """
        To avoid having multiple schemas for the same thing,
            output model when outputting json is either the original model, or a subset of it
        """

        return {
            field_proj: source.__dict__[field_proj]
            for field_proj in field_names
        }

    @staticmethod
    def print_json(obj):
        """
        typer.echo(obj) uses single quotes for strings, resulting in invalid json
        """
        if isinstance(obj, BaseModel):
            obj = obj.dict()
        elif isinstance(obj, list):
            obj = [
                i.dict() if isinstance(i, BaseModel) else i
                for i in obj
            ]

        typer.echo(json.dumps(obj, indent=4))

app = typer.Typer()

aliases_app = typer.Typer()
app.add_typer(aliases_app, name="aliases")

images_app = typer.Typer()
app.add_typer(images_app, name="images")

studies_app = typer.Typer()
app.add_typer(studies_app, name="studies")

reps_app = typer.Typer()
app.add_typer(reps_app, name="representations")

collections_app = typer.Typer()
app.add_typer(collections_app, name="collections")

annotations_app = typer.Typer()
app.add_typer(annotations_app, name="annotations")

filerefs_app = typer.Typer()
app.add_typer(filerefs_app, name="filerefs")


@aliases_app.command("add")
def add_alias(image_uuid: str, name: str, overwrite: bool = False):
    alias = api_models.BIAImageAlias(
        name=name
    )

    persist_image_alias(image_uuid, alias, overwrite=overwrite)


@aliases_app.command("list")
def list_alias(image_uuid: str):
    """
    Accepts either the image uuid, or a (image_alias, accession_id) pair 
    """

    image = get_image(image_uuid)
    image_alias = image.alias.name if image.alias else "NO_ALIAS"

    print(image_alias)

@aliases_app.command("list-for-study")
def list_aliases_for_study(accession_id: str):
    study_images = get_images(accession_id)

    if len(study_images):
        study = get_study(accession_id=accession_id)
        for image in study_images:
            image_alias = image.alias.name if image.alias else "NO_ALIAS"

            typer.echo(f"{image_alias}, {study.accession_id}, {image.uuid}")
    else:
        print(f"Study {accession_id} has no images")


# From https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size 
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


@filerefs_app.command("list")
def list_filerefs(accession_id: str, apply_annotations: bool = True, output: OutputFormat = OutputFormat.PRETTY):
    study_filerefs = get_filerefs(accession_id, apply_annotations=apply_annotations)

    for fileref in study_filerefs:
        readable_size = sizeof_fmt(fileref.size_in_bytes)

        if output == OutputFormat.PRETTY:
            typer.echo(f"{fileref.uuid}, {fileref.name}, {readable_size}, {fileref.type}")
        elif output == OutputFormat.JSON:
            OutputFormat.print_json(
                OutputFormat.fields_project(["uuid", "name", "size_in_bytes", "type"], fileref)
            )

@filerefs_app.command("list-easily-convertable")
def list_easily_convertable_filerefs(accession_id: str):
    bia_study = load_and_annotate_study(accession_id)
    convertable_ext_path = Path(__file__).resolve().parent.parent / "resources" /"bioformats_curated_single_file_formats.txt"
    easily_convertable_exts = [ l for l in convertable_ext_path.read_text().split("\n") if len(l) > 0]
    for fileref in bia_study.file_references:
        if Path(fileref.name).suffix.lower() in easily_convertable_exts:
            readable_size = sizeof_fmt(fileref.size_in_bytes)
            typer.echo(f"{fileref.uuid}, {fileref.name}, {readable_size}")

@images_app.command("list")
def images_list(accession_id: str, output: OutputFormat = OutputFormat.PRETTY):
    images = get_images(accession_id)

    for image in images:
        rep_rep = ','.join(rep.type for rep in image.representations) if image.representations else "NO REPRESENTATIONS"

        if output == OutputFormat.PRETTY:
            typer.echo(f"{image.uuid} {image.original_relpath} {rep_rep}")
        elif output == OutputFormat.JSON:
            OutputFormat.print_json(
                OutputFormat.fields_project(["uuid", "original_relpath", "representations"], image)
            )


@images_app.command("show")
def images_show(
        image_uuid_or_alias: str,
        accession_id: Annotated[Optional[str], typer.Argument(default=None)] = None,
        apply_annotations: bool = True,
        output: OutputFormat = OutputFormat.PRETTY
    ):
    """
    Single argument: Must be the image UUID
    If --accession_id used, then first argument must be Image alias
    """

    img = None
    if accession_id:
        img = get_image_by_alias(accession_id, image_uuid_or_alias, apply_annotations=apply_annotations)
    else:
        UUID(image_uuid_or_alias)
        img = get_image(image_uuid_or_alias, apply_annotations=apply_annotations)

    if output == OutputFormat.PRETTY:
        typer.echo(img.uuid)
        typer.echo(img.original_relpath)
        typer.echo(f"Dimensions: {img.dimensions}")
        typer.echo("Attributes:")
        for k, v in img.attributes.items():
            typer.echo(f"  {k}={v}")
        typer.echo("Representations:")
        for rep in img.representations:
            typer.echo(f"  {rep}")
    elif output == OutputFormat.JSON:
        OutputFormat.print_json(img)
    
@studies_app.command("show")
def show(accession_id: str, output: OutputFormat = OutputFormat.PRETTY):
    study = load_and_annotate_study(accession_id)

    if output == OutputFormat.PRETTY:
        typer.echo(study) # @TODO: Format for human-readable-ness
    elif output == OutputFormat.JSON:
        OutputFormat.print_json(study)

@studies_app.command("recount")
def recount(accession_id: str):
    study_recount(accession_id)

    typer.echo("DONE")

@studies_app.command("list")
def studies_list(output: OutputFormat = OutputFormat.PRETTY):
    studies = get_all_studies()
    study_ids = [f"{study.accession_id}:{study.uuid}" for study in studies]

    if output == OutputFormat.PRETTY:
        typer.echo('\n'.join(sorted(study_ids)))
    elif output == OutputFormat.JSON:
        OutputFormat.print_json(study_ids)


@annotations_app.command("list-study")
def list_study_annotations(accession_id: str):
    annotations = get_study_annotations(accession_id)

    typer.echo(annotations)


@annotations_app.command("create-study")
def create_study_annotation(accession_id: str, key: str, value: str):
    annotation = api_models.StudyAnnotation(
        author_email=get_bia_user(),
        key=key,
        value=value,
        state=api_models.AnnotationState.ACTIVE
    )

    persist_study_annotation(accession_id, annotation)


@annotations_app.command("create-image")
def create_image_annotation(key: str, value: str, image_uuid_or_alias: str, accession_id: Optional[str] = None):    
    image_uuid = image_uuid_or_alias
    if accession_id:
        img = get_image_by_alias(accession_id, image_uuid_or_alias)
        image_uuid = img.uuid

    annotation = api_models.ImageAnnotation(
        author_email=get_bia_user(),
        key=key,
        value=value,
        state=api_models.AnnotationState.ACTIVE
    )

    persist_image_annotation(image_uuid, annotation)


@annotations_app.command("list-image")
def list_image_annotations(image_uuid_or_alias: str, accession_id: Optional[str] = None):    
    img = None
    if accession_id:
        img = get_image_by_alias(accession_id, image_uuid_or_alias)
    else:
        img = get_image(image_uuid_or_alias)
        
    typer.echo(img.annotations)


@annotations_app.command("list-study-tags")
def list_study_tags(accession_id):
    tags = get_study_tags(accession_id)

    typer.echo(tags)


@annotations_app.command("create-study-tag")
def create_study_tag(accession_id, value):
    add_study_tag(accession_id, value)


@reps_app.command("register")
def register_image_representation(accession_id: str, image_id: str, type: str, size: int, uri: str):
    img = get_image_by_alias(accession_id, image_id)
    
    rep = api_models.BIAImageRepresentation(
        size=size,
        uri=[uri],
        type=type,
        dimensions=None,
        attributes={}
    )    
    persist_image_representation(img.uuid, rep)


@reps_app.command("list")
def list_image_representations(accession_id: str, image_id: str):
    img = get_image_by_alias(accession_id, image_id)
    
    reprs = get_representations(img.uuid)

    typer.echo(reprs)

@collections_app.command("list")
def list_collections(output: OutputFormat = OutputFormat.PRETTY):
    collections = get_collections()
    if output == OutputFormat.PRETTY:
        for collection in collections:
            typer.echo(collection)
    elif output == OutputFormat.JSON:
        OutputFormat.print_json(collections)

@collections_app.command("create")
def create_collection(name: str, title: str, subtitle: str, study_uuid_list: str):    
    collection = api_models.BIACollection(
        uuid=str(UUID(int=int(time.time()*1000000))),
        version=0,
        name=name,
        title=title,
        subtitle=subtitle,
        study_uuids=study_uuid_list.split(",")
    )
    persist_collection(collection)


@collections_app.command("add-study")
def add_study_to_collection(collection_name: str, study_uuid: str):
    collection = get_collection(collection_name)
    
    collection.study_uuids.append(study_uuid)

    update_collection(collection)

if __name__ == "__main__":
    app()
