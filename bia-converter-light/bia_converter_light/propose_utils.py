"""Functions to allow proposing images to convert

Propose file references to convert by sorting based on size,
partitioning into n groups and randomly selecting one
file reference from each group
"""

import math
import random
from typing import List, Dict
from pathlib import Path
from bia_converter_light.config import read_only_client
from bia_converter_light.utils import in_bioformats_single_file_formats_list


def select_indicies(n_indicies: int, n_to_select: int = 5) -> list[int]:
    """Select a number of indicies from input list

    Select a number of indicies from input list. Split list into
    n_to_select chunks and randomly select an index from each chunk
    """

    # Seed to allow reproducibility on repeated runs.
    # Note: Only applies to selections after 23/12/2024
    random.seed(42)

    if n_indicies <= n_to_select:
        return list(range(n_indicies))

    min_per_chunk = math.floor(n_indicies / n_to_select)
    remainder = n_indicies % n_to_select
    selected_indicies = []
    stop = -1
    for i in range(n_to_select):
        n_per_chunk = min_per_chunk
        if remainder > 0 and i < remainder:
            n_per_chunk += 1
        start = stop + 1
        stop = start + n_per_chunk - 1
        selected_index = random.randint(start, stop)
        selected_indicies.append(selected_index)
    return selected_indicies


def count_lines(file_path):
    with open(file_path, "r") as file:
        return sum(1 for _ in file)


def read_specific_line(file_path, line_number):
    with open(file_path, "r") as file:
        for current_line_number, line in enumerate(file, start=0):
            if current_line_number == line_number:
                return line  # .strip()
    return None  # If the line number is beyond the end of the file


def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def get_convertible_file_references(accession_id: str) -> List[Dict]:
    """Get details of convertible images for given accession ID"""

    # ToDo: Fix this to recursively call using until all data returned
    PAGE_SIZE_DEFAULT = 10000000

    # Check with LA if there is/will be API call to search by accession_id.
    studies = read_only_client.get_studies(page_size=PAGE_SIZE_DEFAULT)
    study = next((s for s in studies if s.accession_id == accession_id), None)
    if not study:
        return []
    datasets = read_only_client.get_dataset_linking_study(
        study.uuid, page_size=PAGE_SIZE_DEFAULT
    )
    file_references = []
    for dataset in datasets:
        file_references.extend(
            read_only_client.get_file_reference_linking_dataset(
                dataset.uuid, PAGE_SIZE_DEFAULT
            )
        )

    convertible_file_references = [
        {
            "accession_id": accession_id,
            "study_uuid": study.uuid,
            "name": fr.file_path,
            "uuid": fr.uuid,
            "size_in_bytes": fr.size_in_bytes,
            "size_human_readable": sizeof_fmt(fr.size_in_bytes),
        }
        for fr in file_references
        if in_bioformats_single_file_formats_list(fr.file_path)
    ]

    convertible_file_references = sorted(
        convertible_file_references,
        key=lambda fr: (fr["size_in_bytes"], fr["name"]),
        reverse=True,
    )
    return convertible_file_references


def write_convertible_file_references_for_accession_id(
    accession_id: str,
    output_path: Path,
    max_items: int = 5,
    append: bool = True,
) -> int:
    """
    Write details of file references proposed for conversion to file
    """

    convertible_file_references = get_convertible_file_references(accession_id)

    n_proposal_candidates = len(convertible_file_references)
    indicies_to_select = select_indicies(n_proposal_candidates, max_items)

    if append:
        open_text_mode = "a"
    else:
        open_text_mode = "w"

    lines = [
        "\t".join(
            [
                convertible_file_references[i]["accession_id"],
                f"{convertible_file_references[i]['study_uuid']}",
                convertible_file_references[i]["name"],
                f"{convertible_file_references[i]['uuid']}",
                f"{convertible_file_references[i]['size_in_bytes']}",
                convertible_file_references[i]["size_human_readable"],
            ]
        )
        for i in indicies_to_select
    ]
    with output_path.open(open_text_mode) as fid:
        fid.writelines("\n".join(lines))
        # Write a new line so next append starts on next line
        fid.writelines("\n")

    return len(indicies_to_select)
