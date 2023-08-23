"""Test creating thumbnails & other selected functionality in rendering.py

    We test creating thumbnails from multiscales and HCS NGFFs as well as
    other selected functionality of rendering.py. The code for generating
    test images is adapted from the test_reader and test_writer in the 
    ome_zarr_py github repo:
    https://github.com/ome/ome-zarr-py/tree/master/tests.
"""

import numpy as np
import zarr
from ome_zarr.writer import (
    write_image,
    write_multiscale,
    write_multiscales_metadata,
    write_plate_metadata,
    write_well_metadata,
)
from ome_zarr.format import CurrentFormat
from ome_zarr.io import parse_url
from bia_integrator_tools.rendering import NGFFProxyImage, generate_padded_thumbnail_from_ngff_uri

def create_multiscale_image(path, fmt=CurrentFormat()):
    
    store = parse_url(path, mode="w", fmt=fmt).store
    root = zarr.group(store=store)
    group = root.create_group("/", overwrite=True)
    data = np.zeros((1,1,3,256,256))
    for z in range(3):
        data[0,0,z,119:135, 119:135] = (z+1)*10

    # optional rendering settings
    root.attrs["omero"] = {
        "channels": [{
            "color": "00FFFF",
            "window": {"start": 0, "end": 20, "min": 0.0, "max": 255.0},
            "label": "random",
            "active": True,
            "coefficient": 0,
            "family": "ome-ngff",
            "inverted": False,
        }],
        "rdefs":{
            "defaultT": 0,
            "model": "ome-ngff",
            "defaultZ": 1,
        }
    }
 
    write_image(
        image=data,
        group=root,
        fmt=fmt
    )
    root.attrs["multiscales"][0]["metadata"] = {
        "method": "method",
        "version": "2"
    }
    print(root.attrs["multiscales"][0].keys())
    datasets = root.attrs["multiscales"][0]["datasets"].copy()
    axes = root.attrs["multiscales"][0]["axes"].copy()
    version = root.attrs["multiscales"][0]["version"]
    
    write_multiscales_metadata(
        group=root,
        datasets=datasets,
        axes=axes,
        metadata={"method": "method", "version": "2"}
    )

def create_minimal_plate(path, fmt=CurrentFormat()):
    store = parse_url(path, mode="w", fmt=fmt).store
    root = zarr.group(store=store, overwrite=True)
    write_plate_metadata(root, ["A"], ["1"], ["A/1"])
    row_group = root.require_group("A")
    well = row_group.require_group("1")
    write_well_metadata(well, ["0"])
    image = well.require_group("0")
    write_image(np.zeros((1, 1, 4, 256, 256)), image, overwrite=True)

def test_create_ngffproxyimage_from_multiscales():
    create_multiscale_image("test_multiscale.zarr")
    proxy_im = NGFFProxyImage("test_multiscale.zarr")
    assert proxy_im.darray.shape == (1,1,3,256,256) 

def test_generate_padded_thumbnail_from_multiscales():
    #create_multiscale_image("test_multiscale.zarr")
    thumbnail = generate_padded_thumbnail_from_ngff_uri("test_multiscale.zarr")
    assert thumbnail.size == (256,256)

def test_create_ngffproxyimage_from_minimal_plate():
    uri = "test_minimal_plate.zarr"
    create_minimal_plate(uri)
    proxy_im = NGFFProxyImage(uri)
    assert proxy_im.darray.shape == (1,1,4,256,256) 

def test_generate_padded_thumbnail_from_minimal_plate():
    #create_multiscale_image("test_multiscale.zarr")
    thumbnail = generate_padded_thumbnail_from_ngff_uri("test_minimal_plate.zarr")
    assert thumbnail.size == (256,256)
