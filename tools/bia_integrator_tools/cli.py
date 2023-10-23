import logging
from pathlib import Path
from bia_integrator_api import models as api_models
from typing import Optional
from uuid import UUID
import time
from typing_extensions import Annotated

logger = logging.getLogger("biaint")
logging.basicConfig(level=logging.INFO)

import typer

from bia_integrator_core.interface import (
    get_study,
    get_all_studies,
    get_image_by_alias,
    get_image_by_uuid,
    get_images,
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

    image = get_image_by_uuid(image_uuid)
    image_alias = image.alias.name if image.alias else "NO_ALIAS"

    print(image_alias)

@aliases_app.command("list-for-study")
def list_aliases_for_study(accession_id: str):
    study_images = get_images(accession_id)

    if len(study_images):
        study = get_study(accession_id)
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
def list_filerefs(accession_id: str):
    bia_study = load_and_annotate_study(accession_id)

    for fileref in bia_study.file_references:
        readable_size = sizeof_fmt(fileref.size_in_bytes)
        typer.echo(f"{fileref.uuid}, {fileref.name}, {readable_size}, {fileref.type}")

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
def images_list(accession_id: str):
    images = get_images(accession_id)

    for image in images:
        rep_rep = ','.join(rep.type for rep in image.representations) if image.representations else "NO REPRESENTATIONS"
        typer.echo(f"{image.uuid} {image.original_relpath} {rep_rep}")


@images_app.command("show")
def images_show(image_uuid_or_alias: str, accession_id: Annotated[Optional[str], typer.Argument(default=None)] = None):
    """
    Single argument: Must be the image UUID
    Two arguments: Image alias first, then accession_id
    """

    img = None
    if accession_id:
        img = get_image_by_alias(accession_id, image_uuid_or_alias)
    else:
        UUID(image_uuid_or_alias)
        img = get_image_by_uuid(image_uuid_or_alias)

    typer.echo(img.uuid)
    typer.echo(img.original_relpath)
    typer.echo(f"Dimensions: {img.dimensions}")
    typer.echo("Attributes:")
    for k, v in img.attributes.items():
        typer.echo(f"  {k}={v}")
    typer.echo("Representations:")
    for rep in img.representations:
        typer.echo(f"  {rep}")

    
@studies_app.command("show")
def show(accession_id: str):
    study = load_and_annotate_study(accession_id)

    typer.echo(study)

@studies_app.command("recount")
def show(accession_id: str):
    study_recount(accession_id)

    typer.echo("DONE")

@studies_app.command("list")
def list():
    studies = get_all_studies()
    study_accnos = [study.accession_id for study in studies]

    typer.echo('\n'.join(sorted(study_accnos)))


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

    study = get_study(accession_id=accession_id)
    persist_study_annotation(study.uuid, annotation)


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
def create_image_annotation(image_uuid_or_alias: str, accession_id: Optional[str] = None):    
    img = None
    if accession_id:
        img = get_image_by_alias(accession_id, image_uuid_or_alias)
    else:
        img = get_image_by_uuid(image_uuid_or_alias)
        
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
def list_collections():    
    for collection in get_collections():
        typer.echo(collection)

@collections_app.command("create")
def create_collection(name: str, title: str, subtitle: str, accessions_list: str):    
    collection = api_models.BIACollection(
        uuid=str(UUID(int=int(time.time()*1000000))),
        version=0,
        name=name,
        title=title,
        subtitle=subtitle,
        study_uuids=accessions_list.split(",")
    )
    persist_collection(collection)


@collections_app.command("add-study")
def add_study_to_collection(collection_name: str, accession_id: str):
    collection = get_collection(collection_name)
    
    collection.study_uuids.append(accession_id)

    update_collection(collection)

if __name__ == "__main__":
    app()
