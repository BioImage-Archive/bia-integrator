from pathlib import Path
import csv

from scripts.study_filetype_info_to_tsv import combine_study_filetype_info
import bia_integrator_core

current_dir = Path(__name__).resolve().parent
resources_dir = current_dir.parent / "resources"

# Get the expected information
#expected_summary_info = (resources_dir / "study_filetypes_info_to_tsv" / "expected_output" / "study_filetype_info_summary.tsv").read_text()
expected_summary_path = resources_dir / "study_filetypes_info_to_tsv" / "expected_output" / "study_filetype_info_summary.tsv"
with open(expected_summary_path, "r") as fid:
    dict_reader = csv.DictReader(fid, delimiter="\t")
    expected_summary_info = {key: [] for key in dict_reader.fieldnames}
    for row in dict_reader:
        for key, value in row.items():
            # for comparison put numbers as strings
            try:
                expected_summary_info[key].append(str(value))
            except ValueError:
                expected_summary_info[key].append(value)


def test_all_values_equal(monkeypatch):

    monkeypatch.setattr(bia_integrator_core.config.settings, "data_dirpath", resources_dir / 'study_filetypes_info_to_tsv')
    accession_ids = ["S-BIAD106", "S-BIAD661", "S-BSST1047", "S-BSST1053"]
    summary_info = combine_study_filetype_info(accession_ids)

    assert summary_info == expected_summary_info

