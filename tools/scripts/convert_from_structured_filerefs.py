import os
import logging
import tempfile
from pathlib import Path

import typer

from bia_integrator_core.integrator import load_and_annotate_study
from bia_integrator_tools.utils import get_image_rep_by_type
from bia_integrator_tools.io import stage_fileref_and_get_fpath
from bia_integrator_tools.conversion import run_zarr_conversion


logger = logging.getLogger(__file__)


app = typer.Typer()


@app.command('structured-fileref-to-local')
def convert_structured_fileref(accession_id: str, image_id: str, rep_type: str, dst_dir_basepath: str):
    logging.basicConfig(level=logging.INFO)

    bia_study = load_and_annotate_study(accession_id)
    image_rep = get_image_rep_by_type(accession_id, image_id, rep_type)

    n_items = len(image_rep.attributes['structure'])
    dst_dir_basepath = Path(dst_dir_basepath)

    tmpdir_obj = tempfile.TemporaryDirectory()
    tmpdir_path = Path(tmpdir_obj.name)

    for label, fileref_id in image_rep.attributes['structure'].items():
        fileref = bia_study.file_references[fileref_id]
        input_fpath = stage_fileref_and_get_fpath(accession_id, fileref)

        suffix = input_fpath.suffix

        logger.info(f"Linking {input_fpath}")
        target_path = tmpdir_path/(label+suffix)
        target_path.symlink_to(input_fpath)

    pattern_fpath = tmpdir_path / "conversion.pattern"
    pattern = f"Z_<0000-{n_items-1:04d}>{suffix}"
    logger.info(f"Using pattern {pattern}")
    pattern_fpath.write_text(pattern)

    zarr_fpath = dst_dir_basepath/f"{image_id}.zarr"
    logger.info(f"Destination fpath: {zarr_fpath}")
    if not zarr_fpath.exists():
        run_zarr_conversion(pattern_fpath, zarr_fpath)


if __name__ == "__main__":
    app()