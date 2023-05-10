def get_annotation_images_in_study(bia_study):
    """Generate list of images in study that are annotations of another image."""
    
    return [
        image for image in bia_study.images.values()
        if "source image" in image.attributes
    ]


def get_non_annotation_images_in_study(bia_study):
    """Generate list of images in study that are not annotations of another image."""

    return [
        image for image in bia_study.images.values()
        if "source image" not in image.attributes
    ]    