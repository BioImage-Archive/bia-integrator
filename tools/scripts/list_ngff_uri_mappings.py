import typer

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.utils import get_ome_ngff_rep

app = typer.Typer()


@app.command()
def list_ngff_uri_mappings(accession_id: str):

    bia_study = load_and_annotate_study(accession_id)

    possible_ome_ngffs = {
        image_id: get_ome_ngff_rep(image)
        for image_id, image in bia_study.images.items()
    }

    ome_ngff_reps = {
        image_id: rep
        for image_id, rep in possible_ome_ngffs.items()
        if rep
    }

    for image_id, rep in ome_ngff_reps.items():
        print(f"{bia_study.images[image_id].original_relpath}, {rep.uri}")


if __name__ == "__main__":
    app()