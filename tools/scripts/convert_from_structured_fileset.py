"""Convert an image from a structured fileref representation (i.e. multiple input
files together with information on how they relate, such as channel or timepoint
numbers) into OME-Zarr."""

import logging
import tempfile
from pathlib import Path

import typer

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.utils import get_image_rep_by_type
from bia_integrator_tools.io import stage_fileref_and_get_fpath
from bia_integrator_tools.conversion import run_zarr_conversion
from bia_integrator_tools.representations import StructuredFileset

logger = logging.getLogger(__file__)


app = typer.Typer()


def fileref_map_to_pattern(fileref_map):
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

    pattern = f"T<{tmin:04d}-{tmax:04d}>_C<{cmin:04d}-{cmax:04d}>_Z<{zmin:04d}-{zmax:04d}>.tif"

    return pattern


@app.command('structured-fileset-to-local')
def convert_structured_fileset(accession_id: str, image_id: str,  dst_dir_basepath: str):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    image_rep = get_image_rep_by_type(accession_id, image_id, 'structured_fileset')

    assert image_rep, "Can't find image representation"
    sf = StructuredFileset.parse_obj(image_rep.attributes['structured_fileset'])

    # n_items = len(image_rep.attributes['structure'])
    dst_dir_basepath = Path(dst_dir_basepath)

    tmpdir_obj = tempfile.TemporaryDirectory()
    tmpdir_path = Path(tmpdir_obj.name)

    for fileref_id, position in sf.fileref_map.items():
        # print(z, fileref_id)
        t, c, z = position
        label = "T{t:04d}_C{c:04d}_Z{z:04d}".format(z=z, c=c, t=t)

        fileref = bia_study.file_references[fileref_id]
        input_fpath = stage_fileref_and_get_fpath(accession_id, fileref)

        suffix = input_fpath.suffix

        logger.info(f"Linking {input_fpath}")
        target_path = tmpdir_path/(label+suffix)
        target_path.symlink_to(input_fpath)


    pattern = fileref_map_to_pattern(sf.fileref_map)
    pattern_fpath = tmpdir_path / "conversion.pattern"
    logger.info(f"Using pattern {pattern}")
    pattern_fpath.write_text(pattern)

    zarr_fpath = dst_dir_basepath/f"{image_id}.zarr"
    logger.info(f"Destination fpath: {zarr_fpath}")
    if not zarr_fpath.exists():
        run_zarr_conversion(pattern_fpath, zarr_fpath)


if __name__ == "__main__":
    app()