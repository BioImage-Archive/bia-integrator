import os
import logging
import shutil
import subprocess
import platform
import rich
import starfile
from pathlib import Path
from neuroglancer import CoordinateSpace, write_annotations
from pandas import DataFrame

from bia_converter.config import settings
from bia_shared_datamodels import bia_data_model
from bia_integrator_api.models import ImageRepresentation 

logger = logging.getLogger(__name__)


def run_bioformats2raw_with_docker(input_fpath: Path, output_dirpath: Path):
    user_id = os.getuid()
    group_id = os.getgid()

    # We need to map local paths to paths in docker container -> use /tmp in container
    input_dir_map = f"{input_fpath}:/tmp/{input_fpath.name}"
    docker_input_fpath = f"/tmp/{input_fpath.name}"

    output_dir_map = f"{output_dirpath.parent}:/tmp/{output_dirpath.parent.name}"
    docker_output_dirpath = f"/tmp/{output_dirpath.parent.name}/{output_dirpath.name}"

    docker_image = (
        f"openmicroscopy/bioformats2raw:{settings.bioformats2raw_docker_tag} "
    )
    zarr_cmd = (
        f"docker run --rm -u {user_id}:{group_id} -v  {input_dir_map} -v {output_dir_map} "
        + f'{docker_image} "{docker_input_fpath}" "{docker_output_dirpath}"'
    )

    logger.info(f"Converting with {zarr_cmd}")

    retval = subprocess.run(
        zarr_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert (
        retval.returncode == 0
    ), f"Error converting to zarr: {retval.stderr.decode('utf-8')}"


def run_bioformats2raw_with_singularity(input_fpath: Path, output_dirpath: Path):
    docker_image = (
        f"openmicroscopy/bioformats2raw:{settings.bioformats2raw_docker_tag} "
    )
    zarr_cmd = (
        f'singularity run docker://{docker_image} "{input_fpath}" "{output_dirpath}"'
    )

    logger.info(f"Converting with {zarr_cmd}")

    retval = subprocess.run(
        zarr_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert (
        retval.returncode == 0
    ), f"Error converting to zarr: {retval.stderr.decode('utf-8')}"


def run_bioformats2raw_java_cli(input_fpath: Path, output_dirpath: Path):
    zarr_cmd = f'export JAVA_HOME={settings.bioformats2raw_java_home} && {settings.bioformats2raw_bin} "{input_fpath}" "{output_dirpath}"'

    logger.info(f"Converting with {zarr_cmd}")

    retval = subprocess.run(
        zarr_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    assert (
        retval.returncode == 0
    ), f"Error converting to zarr: {retval.stderr.decode('utf-8')}"


def run_zarr_conversion(input_fpath: Path, output_dirpath: Path):
    """Convert the local file at input_fpath to Zarr format, in a directory specified by
    output_dirpath"""

    # Prefer to run with singularity, then docker and lastly with bioformats2raw cli

    # As of 19/03/2025 bioformats2raw docker image only built for linux/amd64.
    # Some of our macs are running arm64 -> run with cli for arm64.
    platform_type = platform.machine().lower()
    arm64_platform = "arm64" in platform_type
    if not arm64_platform and shutil.which("singularity"):
        run_bioformats2raw_with_singularity(input_fpath, output_dirpath)
    elif not arm64_platform and shutil.which("docker"):
        run_bioformats2raw_with_docker(input_fpath, output_dirpath)
    else:
        run_bioformats2raw_java_cli(input_fpath, output_dirpath)


def cached_convert_to_zarr_and_get_fpath(
    image: bia_data_model.Image, input_fpath: Path
):
    dst_dir_basepath = settings.cache_root_dirpath / "zarr"
    dst_dir_basepath.mkdir(exist_ok=True, parents=True)

    zarr_fpath = dst_dir_basepath / f"{image.uuid}.zarr"
    if not zarr_fpath.exists():
        run_zarr_conversion(input_fpath, zarr_fpath)

    return zarr_fpath


def convert_starfile_df_to_json(
        input_fpath: Path, 
        image_pattern: str = None,  
):
    """Convert a STAR file to JSON format, 
    using the image pattern, if given,
    to pull out coordinates for a specific image."""

    star_data = starfile.read(input_fpath)
    rich.print(star_data)


def convert_starfile_df_to_ng_precomp(
        starfile_df: DataFrame, 
        ng_output_dirpath: str, 
        image_rep: ImageRepresentation, 
):

    scales = [
        image_rep.physical_size_z,
        image_rep.physical_size_y,
        image_rep.physical_size_x, 
    ]

    coordinate_space = CoordinateSpace(
        names=['z', 'y', 'x'],
        units=['m', 'm', 'm'],
        scales=scales, 
    )

    writer = write_annotations.AnnotationWriter(
        coordinate_space=coordinate_space,
        annotation_type='point'
    )

    for n, row in starfile_df.iterrows():
        x = int(row.rlnCoordinateX)
        y = int(row.rlnCoordinateY)
        z = int(row.rlnCoordinateZ)

        writer.add_point([z, y, x])

    writer.write(ng_output_dirpath)


