import ast
import json

# BIA image representation types that we add download uris for
DOWNLOADABLE_REPRESENTATIONS = [
    "fire_object",
    "zipped_zarr",
]

# From https://stackoverflow.com/questions/1094841/get-human-readable-version-of-file-size
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def get_annotation_images_in_study(bia_study):
    """Generate list of images in study that are annotations of another image."""
    
    return [
        image for image in bia_study.images.values()
        if "source image" in image.attributes
    ]

def get_annotation_files_in_study(bia_study):
    """Generate list of files in study that are annotations of another image."""
    
    return [
        fileref for fileref in bia_study.file_references.values()
        if "source image" in fileref.attributes
    ]


def get_non_annotation_images_in_study(bia_study):
    """Generate list of images in study that are not annotations of another image."""

    return [
        image for image in bia_study.images.values()
        if "source image" not in image.attributes
    ]

def add_annotation_download_size_attributes(annotation_files):
    """Calculate and add human readable download sizes for annotation files as attribute."""
    for annfile in annotation_files:
        if annfile.size_in_bytes:
            download_size = sizeof_fmt(annfile.size_in_bytes)
        else:
            download_size = "Unavailable"
        annfile.attributes['download_size'] = download_size

    return annotation_files

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
