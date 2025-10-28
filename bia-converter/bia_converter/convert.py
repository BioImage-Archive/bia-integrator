import shutil
import logging
import zipfile
import tempfile
from pathlib import Path
from uuid import UUID

import parse  # type: ignore
from bia_integrator_api.models import (  # type: ignore
    Image,
    ImageRepresentation,
    FileReference,
    Provenance,
    Attribute,
)
from bia_shared_datamodels.package_specific_uuid_creation.image_conversion_uuid_creation import (
    create_image_representation_uuid,
)

from .config import settings
from .io import copy_local_to_s3, stage_fileref_and_get_fpath, sync_dirpath_to_s3
from .conversion import run_zarr_conversion, get_bioformats2raw_version
from .bia_api_client import api_client, store_object_in_api_idempotent
from .rendering import generate_padded_thumbnail_from_ngff_uri
from .utils import (
    create_s3_uri_suffix_for_image_representation,
    create_s3_uri_suffix_for_2d_view_of_image_representation,
    attributes_by_name,
    get_dir_size,
    add_or_update_attribute,
)


logger = logging.getLogger(__file__)


def create_image_representation_object(
    image: Image, conversion_process_dict: dict, image_format: str
) -> ImageRepresentation:
    # Create the base image representation object. Cannot by itself create the file_uri or
    # size attributes correctly

    dataset = api_client.get_dataset(image.submission_dataset_uuid)
    study_uuid = UUID(dataset.submitted_in_study_uuid)
    uuid, uuid_attribute = create_image_representation_uuid(
        study_uuid, conversion_process_dict
    )
    image_rep = ImageRepresentation(
        object_creator=Provenance.BIA_IMAGE_CONVERSION,
        uuid=str(uuid),
        version=0,
        representation_of_uuid=image.uuid,
        # TODO Does image format need to be set?
        image_format=image_format,
        additional_metadata=[
            uuid_attribute.model_dump(),
        ],
        total_size_in_bytes=0,
        file_uri=[],
    )

    return image_rep


def create_2d_image_and_upload_to_s3(ome_zarr_uri, dims, dst_key):
    im = generate_padded_thumbnail_from_ngff_uri(ome_zarr_uri, dims)

    with tempfile.NamedTemporaryFile(suffix=".png") as fh:
        im.save(fh)
        file_uri = copy_local_to_s3(Path(fh.name), dst_key)
        logger.info(f"Wrote thumbnail to {file_uri}")
        size_in_bytes = Path(fh.name).stat().st_size

    return file_uri, size_in_bytes


def convert_interactive_display_to_thumbnail(
    input_image_rep: ImageRepresentation,
) -> str:
    # Should create a 2D thumbnail from convert an INTERACTIVE_DISPLAY rep

    dims = (256, 256)
    # Check the image rep
    assert ".zarr" in input_image_rep.file_uri[0]

    # Retrieve model ibjects
    input_image = api_client.get_image(input_image_rep.representation_of_uuid)

    dst_key = create_s3_uri_suffix_for_2d_view_of_image_representation(
        input_image_rep, dims=dims, name="thumbnail"
    )
    file_uri, size_in_bytes = create_2d_image_and_upload_to_s3(
        input_image_rep.file_uri[0], dims, dst_key
    )

    # Update the BIA Image object with uri for this 2D view
    thumbnail_uri_key = f"{dims[0]}"
    view_details_dict = {
        "provenance": Provenance.BIA_IMAGE_CONVERSION,
        "name": "image_thumbnail_uri",
        "value": {
            thumbnail_uri_key: {
                "uri": file_uri,
                "size": dims[0],
            },
        },
    }
    view_details = Attribute.model_validate(view_details_dict)
    add_or_update_attribute(view_details, input_image.additional_metadata)
    store_object_in_api_idempotent(input_image)

    return file_uri


# TODO - should be able to merge these
def convert_interactive_display_to_static_display(
    input_image_rep: ImageRepresentation,
) -> str:
    # Should convert an INTERACTIVE_DISPLAY rep, to a STATIC_DISPLAY rep

    dims = (512, 512)
    # Check the image rep
    assert ".zarr" in input_image_rep.file_uri[0]

    # Retrieve model ibjects
    input_image = api_client.get_image(input_image_rep.representation_of_uuid)

    dst_key = create_s3_uri_suffix_for_2d_view_of_image_representation(
        input_image_rep, dims=dims, name="static_display"
    )
    file_uri, size_in_bytes = create_2d_image_and_upload_to_s3(
        input_image_rep.file_uri[0], dims, dst_key
    )

    # Update the BIA Image object with uri for this 2D view
    view_details_dict = {
        "provenance": Provenance.BIA_IMAGE_CONVERSION,
        "name": "image_static_display_uri",
        "value": {
            "slice": {
                "uri": file_uri,
                "size": dims[0],
            },
        },
    }
    view_details = Attribute.model_validate(view_details_dict)
    add_or_update_attribute(view_details, input_image.additional_metadata)
    store_object_in_api_idempotent(input_image)

    return file_uri


def get_all_file_references_for_image(image):
    file_references = []
    for fr_uuid in image.original_file_reference_uuid:
        fr = api_client.get_file_reference(fr_uuid)
        file_references.append(fr)

    return file_references


def fileref_map_to_bfconvert_pattern(fileref_map, ext):
    """Determine the pattern needed to enable bioformats to load the components
    of a structured fileset, e.g. for conversion."""

    all_positions = list(fileref_map.values())
    tvals, cvals, zvals = zip(*all_positions)

    zmin = min(zvals)
    zmax = max(zvals)
    cmin = min(cvals)
    cmax = max(cvals)
    tmin = min(tvals)
    tmax = max(tvals)

    pattern = f"T<{tmin:04d}-{tmax:04d}>_C<{cmin:04d}-{cmax:04d}>_Z<{zmin:04d}-{zmax:04d}>{ext}"

    return pattern


def find_file_references_matching_template(file_references, parse_template):
    """
    Match file references against a parsing template to extract dimensional information.

    Iterates through file references and attempts to extract plane (z), time point (t),
    and channel (c) information from their file paths using the provided template.

    Args:
        file_references: Iterable of FileReference objects containing file_path attributes
        parse_template: String template for parse.parse() with optional named fields 'z', 't', 'c'

    Returns:
        tuple: (
            list of matched FileReference objects,
            dict mapping FileReference UUIDs to tuples of (t, c, z) coordinates
        )

    Example:
        file_refs = [FileReference(file_path="image_z01_t02_c03.tif"), ...]
        template = "image_z{z:d}_t{t:d}_c{c:d}.tif"
        matched_refs, coord_map = find_file_references_matching_template(file_refs, template)
        # coord_map[ref.uuid] = (2, 3, 1)  # (t, c, z)
    """

    fileref_map = {}
    selected_filerefs = []
    for fileref in file_references:
        result = parse.parse(parse_template, fileref.file_path)
        if result:
            z = result.named.get("z", 0)
            c = result.named.get("c", 0)
            t = result.named.get("t", 0)
            fileref_map[fileref.uuid] = (t, c, z)
            selected_filerefs.append(fileref)

    return selected_filerefs, fileref_map


def get_shared_extension(filerefs):
    """Get the single shared file extension from a set of file references. If it is not
    unique, fail."""

    extensions = {Path(fileref.file_path).suffix for fileref in filerefs}
    assert len(extensions) == 1
    extension = extensions.pop()

    return extension


def stage_and_link_filerefs(
    tmpdirname, file_references, fileref_coords_map, bfconvert_pattern
):
    """Stage necessary file references to a temporary directory, and symlink them so
    they can be converted with a single command."""

    tmpdir_path = Path(tmpdirname)

    file_references_by_uuid = {fr.uuid: fr for fr in file_references}
    for fileref_id, position in fileref_coords_map.items():
        t, c, z = position
        label = "T{t:04d}_C{c:04d}_Z{z:04d}".format(z=z, c=c, t=t)

        fileref = file_references_by_uuid[fileref_id]
        input_fpath = stage_fileref_and_get_fpath(fileref)

        suffix = input_fpath.suffix

        target_path = tmpdir_path / (label + suffix)
        logger.info(f"Linking {input_fpath} as {target_path}")
        target_path.symlink_to(input_fpath)

    pattern_fpath = tmpdir_path / "conversion.pattern"
    pattern_fpath.write_text(bfconvert_pattern)

    return pattern_fpath


def get_conversion_output_path(output_rep_uuid):
    dst_dir_basepath = settings.cache_root_dirpath / "zarr"
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)
    zarr_fpath = dst_dir_basepath / f"{output_rep_uuid}.zarr"

    return zarr_fpath


def get_dimensions_dict_from_zarr(ome_zarr_image_uri):
    from .proxyimage import ome_zarr_image_from_ome_zarr_uri

    im = ome_zarr_image_from_ome_zarr_uri(ome_zarr_image_uri)
    attr_map = {
        "sizeX": "size_x",
        "sizeY": "size_y",
        "sizeZ": "size_z",
        "sizeC": "size_c",
        "sizeT": "size_t",
        "PhysicalSizeX": "voxel_physical_size_x",
        "PhysicalSizeY": "voxel_physical_size_y",
        "PhysicalSizeZ": "voxel_physical_size_z",
    }

    update_dict = {v: im.__dict__[k] for k, v in attr_map.items()}

    return update_dict


def check_if_path_contains_zarr_group(dirpath: Path) -> bool:
    import zarr

    try:
        zarr.open_group(dirpath, mode="r")
        return True
    except zarr.hierarchy.GroupNotFoundError:
        return False


def fetch_ome_zarr_zip_fileref_and_unzip(
    file_reference: FileReference, output_image_rep: ImageRepresentation
) -> Path:
    """Fetch the given file reference, unzip to a temporary location, copy to
    cache and return the path.

        Args:
        file_reference (FileReference): Reference to the OME-ZARR zip file

    Returns:
        Path: Path to the unzipped directory containing the OME-ZARR data

    Raises:
        zipfile.BadZipFile: If the file is not a valid zip file
    """

    unpacked_zarr_dirpath = get_conversion_output_path(output_image_rep.uuid)

    # If the target directory exists, don't try to overwrite.
    # TODO - some validation that the target directory correctly corresponds to the zip file
    # contents, this is not trivial
    if unpacked_zarr_dirpath.exists():
        logging.info(
            f"Target zarr directory {unpacked_zarr_dirpath} exists, will not overwrite"
        )
        return unpacked_zarr_dirpath

    # Get the file path from the file reference
    zip_path = stage_fileref_and_get_fpath(file_reference)

    # Create a temporary directory to extract to
    temp_dir = Path(tempfile.mkdtemp())

    # Extract the zip file
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)

    # Zarr group root might be same as zip root
    if check_if_path_contains_zarr_group(temp_dir):
        zarr_root = temp_dir

    # Zarr group might be inside a directory
    zip_contents = list(temp_dir.iterdir())
    if len(zip_contents) == 1:
        if check_if_path_contains_zarr_group(zip_contents[0]):
            zarr_root = zip_contents[0]

    logging.info(f"Move {zarr_root} to {unpacked_zarr_dirpath}")

    shutil.move(zarr_root, unpacked_zarr_dirpath)

    return unpacked_zarr_dirpath


def convert_with_bioformats2raw_pattern(
    input_image_rep, file_references, base_image_rep
):
    attrs = attributes_by_name(input_image_rep)
    parse_template = attrs["file_pattern"]["file_pattern"]
    selected_filerefs, fileref_coords_map = find_file_references_matching_template(
        file_references, parse_template
    )
    extension = get_shared_extension(selected_filerefs)
    bfconvert_pattern = fileref_map_to_bfconvert_pattern(fileref_coords_map, extension)
    logger.info(f"Convert with: {bfconvert_pattern}")

    # Fetch the file references to local cache, and link them in the correct structure for conversion
    with tempfile.TemporaryDirectory() as tmpdirname:
        conversion_input_fpath = stage_and_link_filerefs(
            tmpdirname, selected_filerefs, fileref_coords_map, bfconvert_pattern
        )

        # Run the conversion if we need to
        output_zarr_fpath = get_conversion_output_path(base_image_rep.uuid)
        logger.info(f"Converting from {conversion_input_fpath} to {output_zarr_fpath}")
        if not output_zarr_fpath.exists():
            run_zarr_conversion(conversion_input_fpath, output_zarr_fpath)

    return output_zarr_fpath


def convert_uploaded_by_submitter_to_interactive_display(
    input_image_rep: ImageRepresentation, conversion_parameters: dict = {}
) -> ImageRepresentation:
    # Should convert an UPLOADED_BY_SUBMITTER rep, to an INTERACTIVE_DISPLAY rep

    # TODO: Are there any checks with 2025/04 models to ensure the input image rep is as desired?
    # assert input_image_rep.use_type == ImageRepresentationUseType.UPLOADED_BY_SUBMITTER

    image = api_client.get_image(input_image_rep.representation_of_uuid)

    # For unique string for image representation we are using bioformats to raw
    conversion_process_dict = {
        "image_representation_of_submitted_by_uploader": f"{input_image_rep.uuid}",
        "conversion_function": {
            "conversion_function": "bioformats2raw",
            "version": get_bioformats2raw_version(),
        },
        "conversion_config": conversion_parameters,
    }
    base_image_rep = create_image_representation_object(
        image, conversion_process_dict, image_format=".ome.zarr"
    )
    logger.info(
        f"Created image representation for converted image with uuid: {base_image_rep.uuid}"
    )

    # Get the file references we'll need
    file_references = get_all_file_references_for_image(image)

    # TODO: refactor to move extraction of zips to its own function
    if input_image_rep.image_format == ".ome.zarr.zip":
        assert len(file_references) == 1
        output_zarr_fpath = fetch_ome_zarr_zip_fileref_and_unzip(
            file_references[0], base_image_rep
        )
    else:
        try:
            output_zarr_fpath = convert_with_bioformats2raw_pattern(
                input_image_rep, file_references, base_image_rep
            )
        except (KeyError, AssertionError) as e:
            if len(file_references) == 1:
                logger.info(
                    f"Failed to convert using pattern. As image has 1 file reference will attempt to convert from this file reference with file path: {file_references[0].file_path}."
                )
                input_file_path = stage_fileref_and_get_fpath(file_references[0])
                output_zarr_fpath = get_conversion_output_path(f"{base_image_rep.uuid}")
                run_zarr_conversion(input_file_path, output_zarr_fpath)
            else:
                raise e

    # Upload to S3
    dst_suffix = create_s3_uri_suffix_for_image_representation(base_image_rep)
    zarr_group_uri = sync_dirpath_to_s3(output_zarr_fpath, dst_suffix)
    # TODO: Discuss how to handle whether to append '/0'
    # After discussion with MH on 11/02/2025 agreed to default to '/0' (which currently won't work for plate-well)
    ome_zarr_uri = zarr_group_uri + "/0"
    # ome_zarr_uri = zarr_group_uri

    # rich.print(zarr_group_uri)
    # import sys; sys.exit(0)

    # Set image_rep properties that we now know
    # base_image_rep.file_uri =
    base_image_rep.total_size_in_bytes = get_dir_size(output_zarr_fpath)
    base_image_rep.file_uri = [ome_zarr_uri]
    update_dict = get_dimensions_dict_from_zarr(ome_zarr_uri)
    base_image_rep.__dict__.update(update_dict)

    # Write back to API
    store_object_in_api_idempotent(base_image_rep)

    return base_image_rep


def unzip_ome_zarr_archive(
    input_image_rep: ImageRepresentation, conversion_parameters: dict = {}
) -> ImageRepresentation:
    """Unzip an OME-ZARR zip archive image representation to an OME-ZARR"""

    image = api_client.get_image(input_image_rep.representation_of_uuid)

    conversion_process_dict = {
        "image_representation_of_submitted_by_uploader": f"{input_image_rep.uuid}",
        "conversion_function": "unzip_ome_zarr_archive",
        "conversion_config": conversion_parameters,
    }

    base_image_rep = create_image_representation_object(
        image, conversion_process_dict, image_format=".ome.zarr"
    )
    logger.info(
        f"Created image representation for converted image with uuid: {base_image_rep.uuid}"
    )

    # Get the file references we'll need
    file_references = get_all_file_references_for_image(image)

    # TODO: refactor to move extraction of zips to its own function
    if input_image_rep.image_format == ".ome.zarr.zip":
        assert len(file_references) == 1
        output_zarr_fpath = fetch_ome_zarr_zip_fileref_and_unzip(
            file_references[0], base_image_rep
        )
    else:
        raise Exception("Input image representation format {input_image_rep.image_format} is not an OME-ZARR zip archive. Expecting .ome.zarr.zip")

    # Upload to S3
    dst_suffix = create_s3_uri_suffix_for_image_representation(base_image_rep)
    zarr_group_uri = sync_dirpath_to_s3(output_zarr_fpath, dst_suffix)
    # TODO: Discuss how to handle whether to append '/0'
    # After discussion with MH on 11/02/2025 agreed to default to '/0' (which currently won't work for plate-well)
    ome_zarr_uri = zarr_group_uri + "/0"
    # ome_zarr_uri = zarr_group_uri

    # rich.print(zarr_group_uri)
    # import sys; sys.exit(0)

    # Set image_rep properties that we now know
    # base_image_rep.file_uri =
    base_image_rep.total_size_in_bytes = get_dir_size(output_zarr_fpath)
    base_image_rep.file_uri = [ome_zarr_uri]
    update_dict = get_dimensions_dict_from_zarr(ome_zarr_uri)
    base_image_rep.__dict__.update(update_dict)

    # Write back to API
    store_object_in_api_idempotent(base_image_rep)

    return base_image_rep

def update_recommended_vizarr_representation_for_image(image_rep: ImageRepresentation):
    """Update 'recommended_vizarr_representation' attr of underlying Image object"""

    attribute = Attribute.model_validate(
        {
            "provenance": "bia_image_conversion",
            "name": "recommended_vizarr_representation",
            "value": {
                "recommended_vizarr_representation": image_rep.uuid,
            },
        }
    )
    image_uuid = image_rep.representation_of_uuid
    image = api_client.get_image(image_uuid)
    add_or_update_attribute(attribute, image.additional_metadata)
    store_object_in_api_idempotent(image)
