from pathlib import Path

single_file_formats_path = (
    Path(__file__).parent / "resources" / "bioformats_curated_single_file_formats.txt"
)
single_file_formats = [
    s for s in single_file_formats_path.read_text().split("\n") if len(s) > 0
]


def get_image_extension(file_path: str) -> str:
    """Return standardized image extension for a given file path."""

    special_cases = {
        ".ome.zarr.zip": ".ome.zarr.zip",
        ".zarr.zip": ".zarr.zip",
        ".ome.zarr": ".ome.zarr",
        ".ome.tiff": ".ome.tiff",
        ".ome.tif": ".ome.tiff",
        ".tar.gz": ".tar.gz",
    }

    for special_ext, mapped_value in special_cases.items():
        if file_path.lower().endswith(special_ext):
            return mapped_value

    ext_map = {
        ".jpeg": ".jpg",
        ".tiff": ".tif",
    }
    ext = Path(file_path).suffix.lower()
    if ext in ext_map:
        return ext_map[ext]
    else:
        return ext


def extension_in_bioformats_single_file_formats_list(ext: str) -> bool:
    if len(ext) > 1 and not ext[0] == ".":
        ext = "." + ext
    return ext in single_file_formats
