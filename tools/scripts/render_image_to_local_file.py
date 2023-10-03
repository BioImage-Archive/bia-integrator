"""Given an accession identifier and image identifier, load the image and
render to a 2D image, which will be saved to the given local file."""

import typer

from bia_integrator_tools.utils import get_ome_ngff_rep_by_accession_and_image
from bia_integrator_tools.rendering import generate_padded_thumbnail_from_ngff_uri


app = typer.Typer()


@app.command()
def main(accession_id: str, image_id: str, output_fname: str):

    dims = 512, 512

    ome_ngff_rep = get_ome_ngff_rep_by_accession_and_image(accession_id, image_id)

    im = generate_padded_thumbnail_from_ngff_uri(ome_ngff_rep.uri, dims)

    im.save(output_fname)


if __name__ == "__main__":
    app()
