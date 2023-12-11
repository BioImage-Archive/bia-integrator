import typer

from bia_integrator_core.image import get_images
from bia_integrator_tools.utils import get_ome_ngff_rep, list_of_objects_to_dict

app = typer.Typer()


@app.command()
def list_ngff_uri_mappings(accession_id: str):

    images = list_of_objects_to_dict(get_images(accession_id))

    possible_ome_ngffs = {
        image.uuid: get_ome_ngff_rep(image)
        for image in images.values()
    }


    ome_ngff_reps = {
        image_uuid: rep 
        for image_uuid, rep in possible_ome_ngffs.items()
        if rep
    }

    for image_uuid, rep in ome_ngff_reps.items():
        print(f"{images[image_uuid].original_relpath}, {rep.uri}")


if __name__ == "__main__":
    app()