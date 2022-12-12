def get_ome_ngff_rep(image):
    for rep in image.representations:
        if rep.type == "ome_ngff":
            return rep
