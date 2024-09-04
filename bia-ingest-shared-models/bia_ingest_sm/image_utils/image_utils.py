from pathlib import Path
import xml.etree.ElementTree as ET


def get_total_zarr_size(zarr_path: str) -> int:
    """Return size of zarr archive in bytes"""

    # Assume the zarr store is a local disk
    # TODO: Generalise for any uri (including file:// and s3://)
    # TODO: so the argument name for this func should be 'zarr_uri'
    zarr_path = Path(zarr_path)
    return (
        sum(f.stat().st_size for f in zarr_path.rglob("*")) + zarr_path.stat().st_size
    )


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


def get_ome_zarr_pixel_metadata(zarr_location: str) -> dict:
    """Return pixel metadata entry of METADATA.ome.xml of bioformats2raw zarr"""

    # This function assumes the zarr has been created at specified location
    # on disk and was produced by bioformats2raw -> OME/METADATA.ome.xml
    # exists
    #
    # TODO: handle general uris e.g. https://, s3:// or file://
    metadata_path = Path(zarr_location) / "OME" / "METADATA.ome.xml"
    if metadata_path.is_file():
        metadata = parse_xml_string(metadata_path.read_text())
        try:
            pixel_metadata = metadata[
                "{http://www.openmicroscopy.org/Schemas/OME/2016-06}OME"
            ][r"{http://www.openmicroscopy.org/Schemas/OME/2016-06}Image"][
                "{http://www.openmicroscopy.org/Schemas/OME/2016-06}Pixels"
            ]
        except KeyError:
            pixel_metadata = {}
    else:
        pixel_metadata = {}

    return pixel_metadata


# TODO: discuss replacing this function with something from either
#       ome_zarr or ome_zarr_metadata
def parse_xml_string(xml_string: str) -> dict:
    """
    Parse an XML string and convert it into a dictionary.

    This is intended to be used for OME/METADATA.ome.xml created
    by bioformats2raw.
    """

    def _xml_to_dict(element: ET) -> dict:
        """
        Convert XML element and children to a dict, including attributes.
        """
        # Initialize the dictionary to store the element's data
        result = {}

        # Include attributes in the result if they exist
        if element.attrib:
            result.update({k: v for k, v in element.attrib.items()})

        # If the element has no children, return its text or result if there are attributes
        if len(element) == 0:
            return element.text if not result else result

        # Iterate over the children of the element
        for child in element:
            child_dict = _xml_to_dict(child)

            # Handle duplicate tags by storing them as a list
            if child.tag in result:
                if isinstance(result[child.tag], list):
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = [result[child.tag], child_dict]
            else:
                result[child.tag] = child_dict

        return result

    # Parse the XML string into an ElementTree
    root = ET.fromstring(xml_string)

    # Convert the ElementTree into a dictionary
    return {root.tag: _xml_to_dict(root)}
