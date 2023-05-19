import click

from bia_integrator_core.integrator import load_and_annotate_study

from utils import get_annotation_images_in_study, get_non_annotation_images_in_study


@click.command()
@click.argument("accession_id")
def main(accession_id):

    bia_study = load_and_annotate_study(accession_id)

    annotation_images = get_annotation_images_in_study(bia_study)
    non_annotation_images = get_non_annotation_images_in_study(bia_study)

    print(f"Study has {len(annotation_images)} annotations and {len(non_annotation_images)} images")

if __name__ == "__main__":
    main()