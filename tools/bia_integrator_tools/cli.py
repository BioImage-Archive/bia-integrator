import typer

from bia_integrator_core.models import (
    StudyAnnotation,
    BIAImageRepresentation,
    ImageAnnotation,
    BIACollection
)

from bia_integrator_core.interface import (
    get_study,
    get_all_study_identifiers,
    get_image,
    get_images_for_study,
    get_study_annotations,
    persist_study_annotation,
    persist_image_representation,
    persist_image_annotation,
    persist_collection
)



app = typer.Typer()

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


@images_app.command("list")
def images_list(accession_id: str):
    images = get_images_for_study(accession_id)

    for image in images:
        typer.echo(f"{image.id} {image.original_relpath}")


@images_app.command("show")
def images_show(accession_id: str, image_id: str):
    image = get_image(accession_id, image_id)

    typer.echo(image.id)
    typer.echo(image.original_relpath)
    typer.echo("Attributes:")
    for k, v in image.attributes.items():
        typer.echo(f"  {k}={v}")
    typer.echo("Representations:")
    for rep in image.representations:
        typer.echo(f"  {rep}")

    
@studies_app.command("show")
def show(accession_id: str):
    study = get_study(accession_id)

    typer.echo(study)


@studies_app.command("list")
def list():
    studies = get_all_study_identifiers()

    typer.echo('\n'.join(studies))


@annotations_app.command("list-studies")
def list_study_annotations(accession_id: str):
    annotations = get_study_annotations(accession_id)

    typer.echo(annotations)


@annotations_app.command("create-study")
def create_study_annotation(accession_id: str, key: str, value: str):

    annotation = StudyAnnotation(
        accession_id=accession_id,
        key=key,
        value=value
    )

    persist_study_annotation(annotation)


@annotations_app.command("create-image")
def create_image_annotation(accession_id: str, image_id: str, key: str, value: str):
    annotation = ImageAnnotation(
        accession_id=accession_id,
        image_id=image_id,
        key=key,
        value=value
    )

    persist_image_annotation(annotation)


@reps_app.command("register")
def register_image_representation(accession_id: str, image_id: str, type: str, size: int, uri: str):
    rep = BIAImageRepresentation(
        accession_id=accession_id,
        image_id=image_id,
        type=type,
        uri=uri,
        size=size,
        dimensions=None
    )
    persist_image_representation(rep)


@collections_app.command("create")
def create_collection(name: str, title: str, subtitle: str, accessions_list: str):
    collection = BIACollection(
        name=name,
        title=title,
        subtitle=subtitle,
        accession_ids=accessions_list.split(","),
        description=None
    )
    persist_collection(collection)

    


if __name__ == "__main__":
    app()