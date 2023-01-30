from typing import Optional

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import BIAImageRepresentation


def get_ome_ngff_rep(image):
    for rep in image.representations:
        if rep.type == "ome_ngff":
            return rep


def get_ome_ngff_rep_by_accession_and_image(accession_id: str, image_id: str) -> Optional[BIAImageRepresentation]:
    bia_study = load_and_annotate_study(accession_id)
    image = bia_study.images[image_id]
    
    ome_ngff_rep = get_ome_ngff_rep(image)
    
    return ome_ngff_rep