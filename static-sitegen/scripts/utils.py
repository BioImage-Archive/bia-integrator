import ast
import json

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

def format_for_html(to_format: str) -> str:
    """Format the given string for HTML representation."""

    html_mapping = {
        "\n": "<br>",
        # Assumes json is indented by spaces in multiples of 2
        "  ": "&nbsp;&nbsp;",
        '"': "",
        "'": "",
        "[": "",
        "]": "",
    }
    # Allows string to use single quotes.  See balaji k answer in SO
    # https://stackoverflow.com/questions/39491420/python-jsonexpecting-property-name-enclosed-in-double-quotes
    try:
        html = json.dumps(ast.literal_eval(to_format), indent=2)
    except Exception:
        return to_format

    for value, replacement in html_mapping.items():
        html = html.replace(value, replacement)

    return html
