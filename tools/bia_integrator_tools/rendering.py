from typing import Dict, List, Optional

import zarr
import numpy as np
import dask.array as da
from PIL import Image, ImageOps
from pydantic import BaseModel
from microfilm.colorify import multichannel_to_rgb
from matplotlib.colors import LinearSegmentedColormap

from urllib.parse import urlparse
import s3fs

from bia_integrator_tools.utils import get_ome_ngff_rep_by_accession_and_image
from .omezarrmeta import ZMeta


DEFAULT_COLORS = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1],
    [0, 1, 1],
    [1, 0, 1],
    [1, 1, 0]
]

class ChannelRenderingSettings(BaseModel):
    """Rendering settings for a specific channel."""

    label: Optional[str]
    colormap_start: List[float] = [0., 0., 0.]
    colormap_end: List[float]
    window_start: Optional[int]
    window_end: Optional[int]


class RenderingInfo(BaseModel):
    """Rending settings for a whole image."""

    channel_renders: List[ChannelRenderingSettings]
    default_z: Optional[int]
    default_t: Optional[int]


class NGFFProxyImage(object):
    """Helper class for working with remove NGFF images to allow us to access
    size properties of that image, and fetch multiscale data with specific
    resolutions."""

    def __init__(self, uri):
        self.uri = uri
        self.zgroup = open_zarr_wrapper(uri)
        self.array_paths = []
        try:
            self.zgroup.visititems(self._get_array_paths)
        except Exception as e:
            print(f"Exception {e} when trying to get array_paths. Setting array_paths to ['0,']")

        if len(self.array_paths) == 0: self.array_paths = ["0",]

        self._init_darray()
        self.ngff_metadata = ZMeta.parse_obj(self.zgroup.attrs.asdict())
    
    def _get_array_paths(self, name, obj):
        """Get the paths of groups containing array data"""
        if not obj:
            return None
        if "Array" in obj.__str__():
            self.array_paths.append(name)
        elif len(self.array_paths) > 0:
            # We terminate once we have array paths for a subgroup to 
            # prevent recursively traversing groups which may take a while
            # especially when a store has a large number of groups
            return obj
        return None

    @classmethod
    def from_bia_accession_and_image_ids(cls, accession_id, image_id):
        ome_ngff_rep = get_ome_ngff_rep_by_accession_and_image(accession_id, image_id)
        return cls(ome_ngff_rep.uri)


    def _init_darray(self):
        self.darray = dask_array_from_ome_ngff_uri(self.uri, self.array_paths[0])

        # FIXME - this is not a reliable way to determine which dimensions are present in which
        # order, we should be parsing the NGFF metadata to do this

        if len(self.darray.shape) == 5:
            size_t, size_c, size_z, size_y, size_x = self.darray.shape
        elif len(self.darray.shape) == 3:
            size_z, size_y, size_x = self.darray.shape
            size_t = 1
            size_c = 1
        elif len(self.darray.shape) == 2:
            size_y, size_x = self.darray.shape
            size_z = 1
            size_t = 1
            size_c = 1
        else:
            raise Exception("Can't handle this array shape")

        self.size_t = size_t
        self.size_c = size_c
        self.size_z = size_z
        self.size_y = size_y
        self.size_x = size_x

    def get_dask_array_with_min_dimensions(self, dims):
        ydim, xdim = dims
        #path_keys = [dataset.path for dataset in self.ngff_metadata.multiscales[0].datasets]
        path_keys = self.array_paths

        for path_key in reversed(path_keys):
            zarr_array = self.zgroup[path_key]
            if len(self.darray.shape) == 5:
                _, _, _, size_y, size_x = zarr_array.shape
            elif len(self.darray.shape) == 3:
                _, size_y, size_x = zarr_array.shape
            else:
                raise Exception("Can't handle this array shape")

            if (size_y >= ydim) and (size_x >= xdim):
                break
        
        return da.from_zarr(zarr_array)
    
    @property
    def all_sizes(self):
        path_keys = [dataset.path for dataset in self.ngff_metadata.multiscales[0].datasets]

        for path_key in path_keys:
            zarr_array = self.zgroup[path_key]
            yield zarr_array.shape


class BoundingBox2DRel(BaseModel):
    """Bounding box within a plane, described in relative coordniates such that
    1.0 is the full width/height of the plane image."""

    x: float
    y: float
    xsize: float
    ysize: float


class BoundingBox2DAbs(BaseModel):
    """Bounding box within a plane, described in absolute coordinates."""

    x: int
    y: int
    xsize: int
    ysize: int


class PlaneRegionSelection(BaseModel):
    """A 2D rectangular region."""

    t: int
    z: int
    c: int
    bb: BoundingBox2DRel


class RenderingView(BaseModel):
    """A view of a BIAImage that should provide settings to produce a 2D image.
    
    Used for, e.g., generating thumbnails or example images."""

    t: int = 0
    z: int = 0
    region: Optional[PlaneRegionSelection]

    channel_rendering: Dict[int, ChannelRenderingSettings]

def open_zarr_wrapper(uri):
    """Wrapper using s3fs to open a S3 zarr or normal method for file zarr

    """

    if uri.startswith("http"):
        uri_parts = urlparse(uri)
        endpoint_url = f"{uri_parts.scheme}://{uri_parts.netloc}"
        s3_bucket = f"s3:/{uri_parts.path}"
        fs = s3fs.S3FileSystem(anon=True, endpoint_url=endpoint_url)
        return zarr.open(s3fs.S3Map(s3_bucket, s3=fs), mode="r", path=r"/")
    else:
        return zarr.open(uri)


def scale_to_uint8(array):
    """Given an input array, convert to uint8, including scaling to fill the
    0-255 range. 
    
    Primarily used to convert general numpy arrays into an image rendering
    suitable dtype."""

    scaled = array.astype(np.float32)

    if scaled.max() - scaled.min() == 0:
        return np.zeros(array.shape, dtype=np.uint8)

    scaled = 255 * (scaled - scaled.min()) / (scaled.max() - scaled.min())

    return scaled.astype(np.uint8)


def apply_window(array, window_start, window_end):
    """Apply a windowing function to the given array, values above or below
    the window are clipped to the edges, and the range is scaled to the
    window range."""
    
    scaled = (array - window_start) / (window_end - window_start)
    clipped = np.clip(scaled, 0, 1)
    
    return clipped


def generate_channel_renderings(n_channels):
    """Generate a list channel renderings for a number of channels."""

    threemap_ends = [
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]
    ]

    channel_renderings = {
        n: ChannelRenderingSettings(colormap_end=colormap_end)
        for n, colormap_end in enumerate(threemap_ends)
    }

    return channel_renderings


def dask_array_from_ome_ngff_uri(uri, path_key='0'):
    """Get a dask array from a specific OME-NGFF uri"""

    #zgroup = zarr.open(uri)
    fs = s3fs.S3FileSystem(anon=True, endpoint_url="https://uk1s3.embassy.ebi.ac.uk")
    zgroup = open_zarr_wrapper(uri)
    darray = da.from_zarr(zgroup[path_key])

    return darray
    

def dask_array_from_ome_ngff_rep(ome_ngff_rep, path_key='0'):
    """Get a dask array from an OME-NGFF image representation."""

    zgroup = open_zarr_wrapper(ome_ngff_rep.uri)
    darray = da.from_zarr(zgroup[path_key])

    return darray


def pad_to_target_dims(im, target_dims, fill=(0, 0, 0)):
    """Given a PIL Image and a set of target dimensions, pad the image so that
    it fits those dimensions."""

    w, h = im.size

    delta_w = target_dims[0] - w
    delta_h = target_dims[1] - h

    padding = (delta_w//2, delta_h//2, delta_w-(delta_w//2), delta_h-(delta_h//2))
    padded_im = ImageOps.expand(im, padding, fill=fill)

    return padded_im


def select_region_from_dask_array(darray, region):
    """Select a single plane from a Dask array, and compute it."""

    if len(darray.shape) == 5:
        _, _, _, ydim, xdim = darray.shape
    elif len(darray.shape) == 3:
        _, ydim, xdim = darray.shape
    else:
        raise Exception("Can't handle this array shape")
    
    ymin = int(region.bb.y * ydim)
    ymax = int((region.bb.y + region.bb.ysize) * ydim)

    xmin = int(region.bb.x * xdim)
    xmax = int((region.bb.x + region.bb.xsize) * xdim)

    if len(darray.shape) == 5:
        return darray[region.t, region.c, region.z, ymin:ymax, xmin:xmax].compute()
    elif len(darray.shape) == 3:
        return darray[region.z, ymin:ymax, xmin:xmax].compute()
    else:
        raise Exception("Can't handle this array shape")    


def render_multiple_2D_arrays(arrays, colormaps):
    """Given a list of 2D arrays and a list of colormaps, apply each colormap
    merge into a single 2D RGB image."""

    imarray, _, _, _ = multichannel_to_rgb(arrays, colormaps)
    im = Image.fromarray(scale_to_uint8(imarray))
    
    return im


DEFAULT_BB = BoundingBox2DRel(x=0, y=0, xsize=1, ysize=1)


def render_proxy_image(proxy_im, bbrel=DEFAULT_BB, dims=(512, 512), t=None, z=None, csettings=None, mode=None):
    """In order to render a 2D plane we need to:
    
    1. Lazy-load the image as a Dask array.
    2. Select the plane (single t and z values) we'll use.
    3. Separate channels.
    4. Apply a color map to each channel array.
    5. Merge the channel arrays."""

    ydim, xdim = dims

    min_ydim_needed = ydim / bbrel.ysize
    min_xdim_needed = xdim / bbrel.xsize
    
    darray = proxy_im.get_dask_array_with_min_dimensions((min_xdim_needed, min_ydim_needed))

    if not t:
        t = proxy_im.size_t // 2
    if not z:
        z = proxy_im.size_z // 2

    channels_to_render = min(proxy_im.size_c, len(DEFAULT_COLORS))
    if not mode:
        if channels_to_render == 1:
            mode = "grayscale"
        elif channels_to_render == 3:
            mode = "RGB"
        else:
            mode = "channels"

    if not csettings:
        if mode == "grayscale":
            csettings = {
                n: ChannelRenderingSettings(colormap_end=[1, 1, 1])
                for n in range(channels_to_render)
            }            
        else:
            csettings = {
                n: ChannelRenderingSettings(colormap_end=DEFAULT_COLORS[n])
                for n in range(channels_to_render)
            }
    
    region_per_channel = {
        c: PlaneRegionSelection(
            t=t,
            z=z,
            c=c,
            bb=bbrel
        )
        for c in range(channels_to_render)
    }

    channel_arrays = {
        c: select_region_from_dask_array(darray, region)
        for c, region in region_per_channel.items()
    }

    for c, channel_array in channel_arrays.items():
        if csettings[c].window_end:
            windowed_array = apply_window(channel_array, csettings[c].window_start, csettings[c].window_end)
            channel_arrays[c] = windowed_array

    colormaps = {
        c: LinearSegmentedColormap.from_list(f'n{n}', ([0, 0, 0], csetting.colormap_end))
        for n, (c, csetting) in enumerate(csettings.items())
    }

    im = render_multiple_2D_arrays(channel_arrays.values(), list(colormaps.values()))
    
    return im


def generate_padded_thumbnail_from_ngff_uri(ngff_uri, dims=(256, 256), autocontrast=True):
    """Given a NGFF URI, generate a 2D thumbnail of the given dimensions."""

    proxy_im = NGFFProxyImage(ngff_uri)

    im = render_proxy_image(proxy_im)
    im.thumbnail(dims)
    im_rgb = im.convert('RGB')

    if autocontrast:
        cim = ImageOps.autocontrast(im_rgb, (0, 1))
    else:
        cim = im_rgb
        
    padded = pad_to_target_dims(cim, dims)

    return padded

