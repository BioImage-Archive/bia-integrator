import shutil
import logging
import zipfile
import tempfile
import rich
import starfile
import json
from pathlib import Path
from typing import Dict, Tuple
import parse  # type: ignore

from bia_integrator_api.models import (  # type: ignore
    Image, 
    ImageRepresentation,
    ImageRepresentationUseType,
    FileReference,
    AnnotationData, 
    Attribute,
)
from bia_shared_datamodels.uuid_creation import (  # type: ignore
    create_image_representation_uuid,
)

from .config import settings
from .io import copy_local_to_s3, stage_fileref_and_get_fpath, sync_dirpath_to_s3
from .conversion import (
    run_zarr_conversion, 
    convert_starfile_df_to_json, 
    convert_starfile_df_to_ng_precomp, 
)
from .bia_api_client import api_client, store_object_in_api_idempotent, update_object_in_api_idempotent
from .rendering import generate_padded_thumbnail_from_ngff_uri
from .utils import (
    create_s3_uri_suffix_for_image_representation,
    attributes_by_name,
    get_dir_size,
    generate_ng_link_for_zarr_and_precomp_annotation, 
    filter_starfile_df, 
)


logger = logging.getLogger(__file__)
logger.setLevel("INFO")

def create_image_representation_object(image, image_format, use_type):
    # Create the base image representation object. Cannot by itself create the file_uri or
    # size attributes correctly

    image_rep_uuid = create_image_representation_uuid(image, image_format, use_type)
    image_rep = ImageRepresentation(
        uuid=str(image_rep_uuid),
        version=0,
        representation_of_uuid=image.uuid,
        use_type=use_type,
        image_format=image_format,
        attribute=[],
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
) -> ImageRepresentation:
    # Should convert an INTERACTIVE_DISPLAY rep, to a THUMBNAIL rep

    dims = (256, 256)
    # Check the image rep
    assert input_image_rep.use_type == ImageRepresentationUseType.INTERACTIVE_DISPLAY

    # Retrieve model ibjects
    input_image = api_client.get_image(input_image_rep.representation_of_uuid)

    base_image_rep = create_image_representation_object(
        input_image, ".png", "THUMBNAIL"
    )
    logger.info(
        f"Created THUMBNAIL image representation with uuid: {base_image_rep.uuid}"
    )
    w, h = dims
    base_image_rep.size_x = w
    base_image_rep.size_y = h

    dst_key = create_s3_uri_suffix_for_image_representation(base_image_rep)
    file_uri, size_in_bytes = create_2d_image_and_upload_to_s3(
        input_image_rep.file_uri[0], dims, dst_key
    )

    base_image_rep.file_uri = [file_uri]
    base_image_rep.total_size_in_bytes = size_in_bytes

    store_object_in_api_idempotent(base_image_rep)

    return base_image_rep


# TODO - should be able to merge these
def convert_interactive_display_to_static_display(
    input_image_rep: ImageRepresentation,
) -> ImageRepresentation:
    # Should convert an INTERACTIVE_DISPLAY rep, to a STATIC_DISPLAY rep

    dims = (512, 512)
    # Check the image rep
    assert input_image_rep.use_type == ImageRepresentationUseType.INTERACTIVE_DISPLAY

    # Retrieve model ibjects
    input_image = api_client.get_image(input_image_rep.representation_of_uuid)

    base_image_rep = create_image_representation_object(
        input_image, ".png", "STATIC_DISPLAY"
    )
    logger.info(
        f"Created STATIC_DISPLAY image representation with uuid: {base_image_rep.uuid}"
    )
    w, h = dims
    base_image_rep.size_x = w
    base_image_rep.size_y = h

    dst_key = create_s3_uri_suffix_for_image_representation(base_image_rep)
    file_uri, size_in_bytes = create_2d_image_and_upload_to_s3(
        input_image_rep.file_uri[0], dims, dst_key
    )

    base_image_rep.file_uri = [file_uri]
    base_image_rep.total_size_in_bytes = size_in_bytes

    store_object_in_api_idempotent(base_image_rep)

    return base_image_rep


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


def get_conversion_output_path(output_rep):

    input_image = api_client.get_image(output_rep.representation_of_uuid)
    dataset = api_client.get_dataset(input_image.submission_dataset_uuid)
    study = api_client.get_study(dataset.submitted_in_study_uuid)
    zarr_dir = f"{study.accession_id}/{output_rep.representation_of_uuid}/{output_rep.uuid}{output_rep.image_format}"
    dst_dir_basepath = settings.cache_root_dirpath / "zarr"
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)
    zarr_fpath = dst_dir_basepath / zarr_dir

    """
    dst_dir_basepath = settings.cache_root_dirpath / "zarr"
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)
    zarr_fpath = dst_dir_basepath / f"{output_rep.uuid}.zarr"
    """

    return zarr_fpath


def get_annotation_conversion_output_path(
        annotation: AnnotationData, 
        image_uuid: str, 
) -> Path:
    
    image = api_client.get_image(image_uuid)
    dataset = api_client.get_dataset(image.submission_dataset_uuid)
    study = api_client.get_study(dataset.submitted_in_study_uuid)
    ann_dir = f"{study.accession_id}/{image_uuid}/{annotation.uuid}"
    dst_dir_basepath = settings.cache_root_dirpath / "star"
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)
    ann_path = dst_dir_basepath / ann_dir

    return ann_path


def get_annotation_ng_precomp_output_path(
        annotation: AnnotationData, 
        image_uuid: str, 
) -> Path:
    
    image = api_client.get_image(image_uuid)
    dataset = api_client.get_dataset(image.submission_dataset_uuid)
    study = api_client.get_study(dataset.submitted_in_study_uuid)
    ann_dir = f"{study.accession_id}/{image_uuid}/{annotation.uuid}"
    dst_dir_basepath = settings.cache_root_dirpath / "ng_precomp"
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)
    ann_path = dst_dir_basepath / ann_dir

    return ann_path


def process_zarr_metadata(ome_zarr_path, ome_zarr_uri) -> Tuple[Dict, Dict]:
    from .proxyimage import ome_zarr_image_from_ome_zarr_uri
    from .utils import generate_ng_link_for_zarr

    attr_map = {
        "sizeX": "size_x",
        "sizeY": "size_y",
        "sizeZ": "size_z",
        "sizeC": "size_c",
        "sizeT": "size_t",
        "PhysicalSizeX": "physical_size_x",
        "PhysicalSizeY": "physical_size_y",
        "PhysicalSizeZ": "physical_size_z",
    }

    contrast_bounds, physical_sizes, view_position = calculate_zarr_metadata(ome_zarr_path)

    im = ome_zarr_image_from_ome_zarr_uri(ome_zarr_path)
    update_dict = {v: im.__dict__[k] for k, v in attr_map.items()}

    attribute_list = []
    ng_link_dict = {}
    ng_link_value = {}
    ng_link_dict["provenance"] = "bia_conversion"
    ng_link_dict["name"] = "neuroglancer_view_link"
    ng_link_value["neuroglancer_view_link"] = generate_ng_link_for_zarr(ome_zarr_uri, contrast_bounds, view_position, physical_sizes)
    ng_link_dict["value"] = ng_link_value
    attribute_list.append(ng_link_dict)

    #update_dict["attribute"] = attribute_list

    return update_dict, attribute_list


def calculate_zarr_metadata(ome_zarr_path) -> Tuple[Dict, Dict, Tuple]:
    from .proxyimage import ome_zarr_image_from_ome_zarr_uri
    
    im = ome_zarr_image_from_ome_zarr_uri(ome_zarr_path)
    contrast_bounds = (im.ngff_metadata.omero.channels[0].window.min, im.ngff_metadata.omero.channels[0].window.max)
    view_position = (im.sizeZ // 2, im.sizeY // 2, im.sizeX // 2)

    physical_sizes = [1, 1, 1]
    if im.PhysicalSizeX is not None:
        physical_sizes[2] = im.PhysicalSizeX
    if im.PhysicalSizeY is not None:
        physical_sizes[1] = im.PhysicalSizeY
    if im.PhysicalSizeZ is not None:    
        physical_sizes[0] = im.PhysicalSizeZ

    return contrast_bounds, physical_sizes, view_position


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

    unpacked_zarr_dirpath = get_conversion_output_path(output_image_rep)

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
        output_zarr_fpath = get_conversion_output_path(base_image_rep)
        logger.info(f"Converting from {conversion_input_fpath} to {output_zarr_fpath}")
        if not output_zarr_fpath.exists():
            run_zarr_conversion(conversion_input_fpath, output_zarr_fpath)

    return output_zarr_fpath


def convert_uploaded_by_submitter_to_interactive_display(
    input_image_rep: ImageRepresentation, conversion_parameters: dict = {}
) -> ImageRepresentation:
    # Should convert an UPLOADED_BY_SUBMITTER rep, to an INTERACTIVE_DISPLAY rep

    assert input_image_rep.use_type == ImageRepresentationUseType.UPLOADED_BY_SUBMITTER

    image = api_client.get_image(input_image_rep.representation_of_uuid)
    base_image_rep = create_image_representation_object(
        image, ".ome.zarr", "INTERACTIVE_DISPLAY"
    )
    logger.info(
        f"Created INTERACTIVE_DISPLAY image representation with uuid: {base_image_rep.uuid}"
    )

    # Get the file references we'll need
    file_references = get_all_file_references_for_image(image)

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
        except AssertionError as e:
            if len(file_references) == 1:
                logger.info(
                    f"Failed to convert using pattern. As image has 1 file reference will attempt to convert from this file reference with file path: {file_references[0].file_path}."
                )
                input_file_path = stage_fileref_and_get_fpath(file_references[0])
                output_zarr_fpath = get_conversion_output_path(base_image_rep)
                run_zarr_conversion(input_file_path, output_zarr_fpath)
            else:
                raise e

    # TODO: Discuss how to handle whether to append '/0'
    # After discussion with MH on 11/02/2025 agreed to default to '/0' (which currently won't work for plate-well)
    
    # ome_zarr_uri = zarr_group_uri

    # rich.print(zarr_group_uri)
    # import sys; sys.exit(0)

    # Set image_rep properties that we now know
    # base_image_rep.file_uri =

    if settings.local:
        ome_zarr_path = str(output_zarr_fpath) + "/0"
        ome_zarr_uri = f"http://localhost:8081/images/{base_image_rep.uuid}{base_image_rep.image_format}/0"
    else:
        dst_suffix = create_s3_uri_suffix_for_image_representation(base_image_rep)
        zarr_group_uri = sync_dirpath_to_s3(output_zarr_fpath, dst_suffix)
        ome_zarr_path = zarr_group_uri + "/0"
        ome_zarr_uri = ome_zarr_path

    base_image_rep = update_ome_zarr_image_rep(
        base_image_rep, output_zarr_fpath, ome_zarr_uri, ome_zarr_path
    )

    # Write back to API
    store_object_in_api_idempotent(base_image_rep)

    return base_image_rep


def update_ome_zarr_image_rep(
    base_image_rep: ImageRepresentation, 
    output_zarr_fpath: Path, 
    ome_zarr_uri: str, 
    ome_zarr_path: str, 
) -> ImageRepresentation:
    
    base_image_rep.total_size_in_bytes = get_dir_size(output_zarr_fpath)
    base_image_rep.file_uri = [ome_zarr_uri]
    update_dict, attributes = process_zarr_metadata(ome_zarr_path, ome_zarr_uri)
    base_image_rep.__dict__.update(update_dict)
    base_image_rep.attribute = attributes

    return base_image_rep


def convert_star_annotation_to_json(
        annotation: AnnotationData, 
        image_rep: ImageRepresentation, 
        image_uuid: str,  
        fpath: Path, 
):
    
    # TODO: assumption of use type of image rep? Certainly interactive display, but uploaded by submitter could also be OME-Zarr.
    # (though the latter would not currently be linked in any way to annotation data...)

    star_df = starfile.read(fpath)
    filtered_df = filter_starfile_df(star_df, annotation, image_uuid)

    data_list = filtered_df.to_dict(orient='records')
    output_path = get_annotation_conversion_output_path(annotation, image_uuid)
    output_path.mkdir(exist_ok=True, parents=True)
    output_file = output_path / "annotation_data.json"
    with open(output_file, 'w') as f:
        json.dump(data_list, f, indent=2)
    
    if "annotation_file_paths" in attrs:
        annotation_file_paths = attrs["annotation_file_paths"]["annotation_file_paths"]
    else:
        annotation_file_paths = []
    annotation_file_paths.append({image_uuid: str(output_file)})

    current_attributes = annotation.attribute
    new_attributes = Attribute(
        name="annotation_file_paths", 
        value={"annotation_file_paths": annotation_file_paths}, 
        provenance="bia_conversion"
    )
    annotation.attribute = current_attributes + [new_attributes]

    ng_output_path = get_annotation_ng_precomp_output_path(annotation, image_uuid)
    convert_starfile_df_to_ng_precomp(selected_df, ng_output_path, image_rep)
    
    if "ng_precomp_file_paths" in attrs:
        ng_precomp_file_paths = attrs["ng_precomp_file_paths"]["ng_precomp_file_paths"]
    else:
        ng_precomp_file_paths = []
    ng_precomp_file_paths.append({image_uuid: str(ng_output_path)})

    current_attributes = annotation.attribute
    new_attributes = Attribute(
        name="ng_precomp_file_paths", 
        value={"ng_precomp_file_paths": ng_precomp_file_paths}, 
        provenance="bia_conversion"
    )
    annotation.attribute = current_attributes + [new_attributes]
    
    starfile_uri = f"http://localhost:8081/annotations/{annotation.uuid}"
    contrast_bounds, physical_sizes, position = calculate_zarr_metadata(f"{image_rep.file_uri[0]}")

    state_uri = generate_ng_link_for_zarr_and_precomp_annotation(
        image_rep.file_uri[0],  
        starfile_uri, 
        contrast_bounds,
        position,
        physical_sizes,  
    )

    rich.print(f"state uri: {state_uri}")
    
    image, image_rep = update_annotated_image_and_image_rep(
        image_uuid, 
        image_rep, 
        state_uri
    )

    update_object_in_api_idempotent(image)
    update_object_in_api_idempotent(image_rep)
    update_object_in_api_idempotent(annotation)


def update_annotated_image_and_image_rep(
    image_uuid: str, 
    image_rep: ImageRepresentation, 
    ng_uri_link: str, 
) -> tuple[Image, ImageRepresentation]:
    
    current_rep_attributes = image_rep.attribute
    new_attributes = Attribute(
        name="neuroglancer_view_link", 
        value={"neuroglancer_view_link": ng_uri_link}, 
        provenance="bia_conversion"
    )
    image_rep.attribute = current_rep_attributes + [new_attributes]

    image = api_client.get_image(image_uuid)
    current_img_attributes = image.attribute
    new_attributes = Attribute(
        name="preferred_neuroglancer_image_representation_uuid", 
        value={"preferred_neuroglancer_image_representation_uuid": image_rep.uuid}, 
        provenance="bia_conversion"
    )
    image.attribute = current_img_attributes + [new_attributes]

    return image, image_rep