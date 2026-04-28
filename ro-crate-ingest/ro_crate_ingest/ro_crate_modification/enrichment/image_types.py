from enum import Enum


class ImageType(str, Enum):
    """
    Controlled vocabulary for the image types that can appear in a track.
    """
    FRAMES = "frames"
    TILT_SERIES = "tilt_series"
    ALIGNED_TILT_SERIES = "aligned_tilt_series"
    TOMOGRAM = "tomogram"
    DENOISED_TOMOGRAM = "denoised_tomogram"
    SEGMENTATION = "segmentation"
