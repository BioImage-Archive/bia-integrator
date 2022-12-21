import os
import uuid
import logging
import tempfile
from pathlib import Path

import click
import shutil
import requests
from pydantic import BaseSettings


from bia_integrator_tools.conversion import run_zarr_conversion
from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_core.models import BIAImageRepresentation
from bia_integrator_core.interface import persist_image_representation


logger = logging.getLogger(__file__)


# COMPANION_TEMPLATE = """<?xml version='1.0' encoding='utf-8'?>
# <OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06" xmlns:OME="http://www.openmicroscopy.org/Schemas/OME/2016-06" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd">
#   <Image ID="Image:0" Name="{image_name}">
#     <Pixels DimensionOrder="XYZCT" ID="Pixels:0:0" SizeC="1" SizeT="1" SizeX="{size_x}" SizeY="{size_y}" SizeZ="{size_z}" Type="{dtype}">
#       <TiffData FirstC="0" FirstT="0" FirstZ="0" PlaneCount="{n_planes}">
#         <UUID FileName="{filename}">urn:uuid:{uuid}</UUID>
#       </TiffData>
#     </Pixels>
#   </Image>
# </OME>
# """

COMPANION_TEMPLATE = """<?xml version='1.0' encoding='utf-8'?>
<OME xmlns="http://www.openmicroscopy.org/Schemas/OME/2016-06" xmlns:OME="http://www.openmicroscopy.org/Schemas/OME/2016-06" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.openmicroscopy.org/Schemas/OME/2016-06 http://www.openmicroscopy.org/Schemas/OME/2016-06/ome.xsd">
  <Image ID="Image:0" Name="{image_name}">
    <Pixels DimensionOrder="XYZCT" ID="Pixels:0:0" SizeC="1" SizeT="1" SizeX="{size_x}" SizeY="{size_y}" SizeZ="{size_z}" Type="uint16">
      <TiffData FirstC="0" FirstT="0" FirstZ="0" PlaneCount="{n_planes}">
        <UUID FileName="{filename}">urn:uuid:{uuid}</UUID>
      </TiffData>
    </Pixels>
  </Image>
</OME>
"""

@click.command()
@click.argument("input_fpath")
def main(input_fpath):

    import sys; sys.exit(0)

    logging.basicConfig(level=logging.INFO)

    from imageio import volread

    vol = volread(input_fpath)

    size_x, size_y, size_z = vol.shape
    n_planes=size_z

    fname = Path(input_fpath).name

    companion_str = COMPANION_TEMPLATE.format(
        image_name=fname,
        size_x=size_x,
        size_y=size_y,
        size_z=size_z,
        n_planes=n_planes,
        dtype=vol.dtype,
        filename=fname,
        uuid=uuid.uuid1()
    )


    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        tmpfpath = tmpdir_path/"tmp.companion.ome"
        os.symlink(input_fpath, tmpdir_path/fname)
        with open(tmpfpath, "w") as fh:
            fh.write(companion_str)
        run_zarr_conversion(tmpfpath, "tmp/IM2.zarr")


if __name__ == "__main__":
    main()