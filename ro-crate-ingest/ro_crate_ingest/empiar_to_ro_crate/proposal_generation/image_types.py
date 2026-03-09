from enum import Enum
from typing import NamedTuple


class ImageType(str, Enum):
    """
    Controlled vocabulary for the image types that can appear in a track.
    """
    FRAMES = "frames"
    TILT_SERIES = "tilt_series"
    ALIGNED_TILT_SERIES = "aligned_tilt_series"
    TOMOGRAM = "tomogram"
    DENOISED_TOMOGRAM = "denoised_tomogram"


class ImageTypeSpec(NamedTuple):
    """
    Per-ImageType configuration for the general assigned_image builder.

    image_type       : the ImageType being built
    upstream_types   : ordered preference list of upstream ImageTypes to use
                       as input linkage (excluding frames, which is handled
                       separately via label_prefix). Frames are always tried
                       last if all upstream_types are absent.
    """
    image_type: ImageType
    upstream_types: list[ImageType]


# Defines the input linkage chain for each non-frames ImageType, preferred first.
IMAGE_TYPE_SPECS: list[ImageTypeSpec] = [
    ImageTypeSpec(ImageType.TILT_SERIES,         []),
    ImageTypeSpec(ImageType.ALIGNED_TILT_SERIES, [ImageType.TILT_SERIES]),
    ImageTypeSpec(ImageType.TOMOGRAM,            [ImageType.ALIGNED_TILT_SERIES, ImageType.TILT_SERIES]),
    ImageTypeSpec(ImageType.DENOISED_TOMOGRAM,   [ImageType.ALIGNED_TILT_SERIES, ImageType.TILT_SERIES]),
]
