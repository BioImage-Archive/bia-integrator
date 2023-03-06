import logging

from PIL import Image, ImageOps
import numpy as np
from ome_zarr.io import parse_url
from ome_zarr.reader import Reader
from bia_integrator_tools.utils import get_ome_ngff_rep
from bia_integrator_core.integrator import load_and_annotate_study
from microfilm.colorify import multichannel_to_rgb
from matplotlib.colors import LinearSegmentedColormap


logger = logging.getLogger("thumbnailer")


def get_zarr_uri(accession_id: str, image_id: str) -> str:
    bia_study = load_and_annotate_study(accession_id)
    image = bia_study.images[image_id]
    
    ome_ngff_rep = get_ome_ngff_rep(image)
    
    return ome_ngff_rep.uri


def scale_to_uint8(array):

    scaled = array.astype(np.float32)

    if scaled.max() - scaled.min() == 0:
        return np.zeros(array.shape, dtype=np.uint8)

    scaled = 255 * (scaled - scaled.min()) / (scaled.max() - scaled.min())

    return scaled.astype(np.uint8)


def highest_res_image_from_zarr_uri(zarr_uri):

    # store = parse_url(zarr_uri, mode="r").store

    reader = Reader(parse_url(zarr_uri))
    # nodes may include images, labels etc
    nodes = list(reader())
    # first node will be the image pixel data
    image_node = nodes[0]

    highest_res = image_node.data[0]
    
    return highest_res


def min_dim_array_from_zarr_uri(zarr_uri, dimensions):

    min_x, min_y = dimensions

    reader = Reader(parse_url(zarr_uri))
    # nodes may include images, labels etc
    nodes = list(reader())
    # first node will be the image pixel data
    image_node = nodes[0]

    for array in reversed(image_node.data):

        if len(array.shape) == 5:
            size_t, size_c, size_z, size_y, size_x = array.shape
        if len(array.shape) == 3:
            size_z, size_y, size_x = array.shape
        
        if (size_x >= min_x) and (size_y >= min_y):
            return array
        
    return image_node.data[0]
        

from matplotlib.colors import LinearSegmentedColormap


def zarr_uri_to_image_array(zarr_uri: str) -> np.array:
    
    highest_res = highest_res_image_from_zarr_uri(zarr_uri)

    size_t, size_c, size_z, size_y, size_x = highest_res.shape

    CMAPS = [
        'pure_magenta',
        'pure_green',
        'pure_blue',
        'pure_cyan',
        'pure_yellow'
    ]

    CMAPS = [
        my_cmap,
        'pure_yellow'
    ]

    t = size_t // 2
    z = size_z // 2

    channel_images = [
        highest_res[t,c,z,:,:].compute()
        for c in range(size_c)
    ]

    imarray, cmap_objs, cmaps, image_min_max = multichannel_to_rgb(channel_images, CMAPS[:size_c])
    
    return imarray


def thumbnail_from_image(accession_id: str, image_id: str, dimensions=(256, 256)) -> Image:
    
    zarr_uri = get_zarr_uri(accession_id, image_id)
    imarray = zarr_uri_to_image_array(zarr_uri)
    
    im = Image.fromarray(scale_to_uint8(imarray))
    im.thumbnail(dimensions)
    
    return im


def pad_to_target_dims(im, target_dims, fill=(0, 0, 0)):

    w, h = im.size

    delta_w = target_dims[0] - w
    delta_h = target_dims[1] - h

    padding = (delta_w//2, delta_h//2, delta_w-(delta_w//2), delta_h-(delta_h//2))
    padded_im = ImageOps.expand(im, padding, fill=fill)
    
    return padded_im


def get_single_channel_image_arrays(imarray, z=None, t=None):

    if len(imarray.shape) == 5:
        size_t, size_c, size_z, size_y, size_x = imarray.shape
        if not t:
            t = size_t // 2
        if not z:
            z = size_z // 2
        channel_images = [
            imarray[t,c,z,:,:].compute()
            for c in range(size_c)
        ]
    if len(imarray.shape) == 3:
        size_z, size_y, size_x = imarray.shape

        if not z:
            z = size_z // 2
        channel_images = [
            imarray[z,:,:].compute()
        ]

    



    
    return channel_images


def channel_render_to_cmap(ch_render, name):
    
    return LinearSegmentedColormap.from_list(name, (ch_render.colormap_start, ch_render.colormap_end))


def channel_arrays_and_chrenders_to_thumbnail(channel_arrays, channel_renders, target_dims):
    
    cmaps = [
        channel_render_to_cmap(ch_render, f"ch{n}")
        for n, ch_render in enumerate(channel_renders, start=1)
    ]
    
    size_c = len(channel_arrays)
    imarray, _, _, _ = multichannel_to_rgb(channel_arrays, cmaps[:size_c])

    im = Image.fromarray(scale_to_uint8(imarray))
    im.thumbnail(target_dims)
    thumbnail_im = pad_to_target_dims(im, target_dims)
    
    return thumbnail_im


def scale_factor_and_clip(imarray, factor):

    srange = factor * (imarray.max() - imarray.min())
    smin = imarray.min()

    scaled_float = (imarray - smin) / srange
    clipped_float = np.clip(scaled_float, 0, 1)
    scaled_uint8 = (255 * clipped_float).astype(np.uint8)

    return scaled_uint8


def scale_channel_arrays(channel_arrays, channel_renders):
    
    scale_factors = [
        channel_render.scale_factor
        for channel_render in channel_renders
    ]

    scaled_arrays = [
        scale_factor_and_clip(imarray, scale_factor)
        for imarray, scale_factor in zip(channel_arrays, scale_factors)
    ]
    
    return scaled_arrays