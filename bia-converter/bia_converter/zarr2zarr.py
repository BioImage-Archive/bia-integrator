import math
from typing import List, Optional, Annotated
from pathlib import Path

import zarr
import rich
import typer
from pydantic import BaseModel, Field

from .proxyimage import ome_zarr_image_from_ome_zarr_uri
from .omezarrgen import (
    rechunk_and_save_array,
    create_ome_zarr_metadata,
    downsample_array_and_write_to_dirpath,
)


app = typer.Typer()


def calculate_downsampling_steps(shape):
    max_dim = max(shape)
    steps = math.ceil(math.log2(max_dim / 256))
    return max(0, steps)


@app.command()
def zarr_group_info(zarr_uri):
    group = zarr.open_group(zarr_uri)
    for k in group.array_keys():
        ar = group[k]
        rich.print(f"Key: {k}, shape: {ar.shape}, chunks: {ar.chunks}")


@app.command()
def ome_zarr_info(ome_zarr_uri):
    im = ome_zarr_image_from_ome_zarr_uri(ome_zarr_uri)

    rich.print(im)


class ZarrConversionConfig(BaseModel):
    target_chunks: List[int] = Field(
        default=[1, 1, 64, 64, 64], description="Array chunk layout for output zarr"
    )
    downsample_factors: List[int] = Field(
        default=[1, 1, 2, 2, 2],
        description="Factor by which each successive pyramid layer will be downsampled",
    )
    transpose_axes: List[int] = Field(
        default=[0, 1, 2, 3, 4],
        description="Order of axis transpositions to be applied during transformation.",
    )
    coordinate_scales: List[float] = Field(
        default=None,
        description="Voxel to physical space coordinate scales for pyramid base level. If unset, will be copied from input OME-Zarr",
    )
    n_pyramid_levels: int = Field(default=None, description="Number of downsampled ")
    rewrite_omero_block: bool = Field(
        default=False,
        description="Rewrite the OMERO rendering block, guessing parameters. Otherwise will copy from input OME-Zarr.",
    )
    zarr_version: int = Field(
        default=2, description="Version of Zarr to use for output (2 or 3)"
    )
    shard_size: List[int] = Field(
        default=[1, 1, 128, 128, 128], description="Sharding size to use for Zarr v3"
    )


def coordinate_scales_from_ome_zarr_uri(ome_zarr_uri: str):
    im = ome_zarr_image_from_ome_zarr_uri(ome_zarr_uri)
    from .proxyimage import calculate_voxel_to_physical_factors

    sf = calculate_voxel_to_physical_factors(im.ngff_metadata)
    coordinate_scales = [
        1.0,
        1.0,
        sf["PhysicalSizeZ"],
        sf["PhysicalSizeY"],
        sf["PhysicalSizeX"],
    ]

    return coordinate_scales


def n_pyramid_levels_from_ome_zarr_uri(ome_zarr_uri: str):
    im = ome_zarr_image_from_ome_zarr_uri(ome_zarr_uri)

    return im.n_scales


@app.command()
def zarr2zarr(
    ome_zarr_uri: str,
    output_base_dirpath: Path,
    conversion_config: Annotated[Optional[str], typer.Argument()] = "{}",
):
    config = ZarrConversionConfig.model_validate_json(conversion_config)
    if not config.coordinate_scales:
        config.coordinate_scales = coordinate_scales_from_ome_zarr_uri(ome_zarr_uri)
    if not config.n_pyramid_levels:
        config.n_pyramid_levels = n_pyramid_levels_from_ome_zarr_uri(ome_zarr_uri)

    rich.print(config)

    output_array_keys = [str(i) for i in range(config.n_pyramid_levels)]

    # Rechunk the base of the pyramid
    # FIXME - path key for base of incoming pyramid is not always '0', just usually
    input_array_uri = ome_zarr_uri + "/0"
    output_dirpath = output_base_dirpath / "0"
    if not output_dirpath.exists():
        rechunk_and_save_array(
            input_array_uri, output_dirpath, config.target_chunks, config.transpose_axes
        )

    # Regenerate the rest of the period by downsampling
    for level in range(config.n_pyramid_levels - 1):
        input_array_dirpath = output_base_dirpath / output_array_keys[level]
        output_array_dirpath = output_base_dirpath / output_array_keys[level + 1]
        if not output_array_dirpath.exists():
            rich.print(
                f"Downsampling from {input_array_dirpath} to {output_array_dirpath}"
            )
            downsample_array_and_write_to_dirpath(
                str(input_array_dirpath),
                output_array_dirpath,
                config.downsample_factors,
                config.target_chunks,
            )

    # Create and write the OME-Zarr metadata
    ome_zarr_metadata = create_ome_zarr_metadata(
        str(output_base_dirpath),
        "test_name",
        config.coordinate_scales,
        config.downsample_factors,
    )
    group = zarr.open_group(output_base_dirpath)
    group.attrs.update(ome_zarr_metadata.model_dump(exclude_unset=True))  # type: ignore


@app.command()
def n52zarr(
    n5_uri: str,
    output_base_dirpath: Path,
    conversion_config: Annotated[Optional[str], typer.Argument()] = "{}",
):
    # n5_uri = "https://s3.embl.de/platybrowser/rawdata/sbem-6dpf-1-whole-raw.n5/setup0/timepoint0/s0"

    import tensorstore as ts

    dataset = ts.open({"driver": "n5", "kvstore": n5_uri}).result()

    # TODO - this is hacky, assumes 3 dimensions always z, y, x
    if len(dataset.shape) == 3:
        output_array = dataset[None, None, :, :, :]
    else:
        output_array = dataset

    from .omezarrgen import write_array_to_disk_chunked

    config = ZarrConversionConfig.model_validate_json(conversion_config)
    if not config.coordinate_scales:
        config.coordinate_scales = [1.0, 1.0, 1.0, 1.0, 1.0]
    if not config.n_pyramid_levels:
        config.n_pyramid_levels = 1 + calculate_downsampling_steps(dataset.shape)

    rich.print(config)

    output_dirpath = output_base_dirpath / "0"
    if not output_dirpath.exists():
        write_array_to_disk_chunked(output_array, output_dirpath, config.target_chunks)
    else:
        rich.print(f"{output_dirpath} exists, will not overwrite")

    # Regenerate the rest of the period by downsampling
    output_array_keys = [str(i) for i in range(config.n_pyramid_levels)]
    for level in range(config.n_pyramid_levels - 1):
        input_array_dirpath = output_base_dirpath / output_array_keys[level]
        output_array_dirpath = output_base_dirpath / output_array_keys[level + 1]
        if not output_array_dirpath.exists():
            rich.print(
                f"Downsampling from {input_array_dirpath} to {output_array_dirpath}"
            )
            downsample_array_and_write_to_dirpath(
                str(input_array_dirpath),
                output_array_dirpath,
                config.downsample_factors,
                config.target_chunks,
            )

    # Create and write the OME-Zarr metadata
    ome_zarr_metadata = create_ome_zarr_metadata(
        str(output_base_dirpath),
        "test_name",
        config.coordinate_scales,
        config.downsample_factors,
    )
    group = zarr.open_group(output_base_dirpath)
    group.attrs.update(ome_zarr_metadata.model_dump(exclude_unset=True))  # type: ignore


if __name__ == "__main__":
    app()
