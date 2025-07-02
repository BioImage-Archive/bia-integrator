"""Functions to allow proposing images to convert

Propose file references to convert by sorting based on size,
partitioning into n groups and randomly selecting one
file reference from each group
"""

import math
import random
from typing import List, Dict
from pathlib import Path
import csv
from ruamel.yaml import YAML
from bia_shared_datamodels import bia_data_model
from bia_assign_image.api_client import get_api_client, ApiTarget
from bia_assign_image.utils import (
    in_bioformats_single_file_formats_list,
    get_all_api_results,
    get_value_from_attribute_list,
)


def dataset_has_image_creation_prerequisites(dataset: bia_data_model.Dataset) -> bool:
    """Assume we need biosample, image acquisition and specimen preparation protocols"""

    image_acquisition_protocol_uuid = get_value_from_attribute_list(
        dataset.additional_metadata, "image_acquisition_protocol_uuid"
    )
    image_preparation_protocol_uuid = get_value_from_attribute_list(
        dataset.additional_metadata, "specimen_imaging_preparation_protocol_uuid"
    )
    bio_sample_uuid = get_value_from_attribute_list(
        dataset.additional_metadata, "bio_sample_uuid"
    )
    image_pre_requisites = [
        len(image_acquisition_protocol_uuid),
        len(image_preparation_protocol_uuid),
        len(bio_sample_uuid),
    ]
    return all(image_pre_requisites)


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


def get_convertible_file_references(
    accession_id: str,
    api_target: ApiTarget,
    check_image_creation_prerequisites: bool = True,
    include_annotation_details: bool = False,
) -> List[Dict]:
    """Get details of convertible images for given accession ID"""

    api_client = get_api_client(api_target)
    study = api_client.search_study_by_accession(accession_id)
    if not study:
        return []
    datasets = get_all_api_results(
        uuid=study.uuid,
        api_method=api_client.get_dataset_linking_study,
        page_size_setting=20,
    )

    convertible_file_references = []

    for dataset in datasets:
        if check_image_creation_prerequisites:
            if not dataset_has_image_creation_prerequisites(dataset):
                continue

        file_references: list[bia_data_model.FileReference] = get_all_api_results(
            uuid=dataset.uuid,
            api_method=api_client.get_file_reference_linking_dataset,
            page_size_setting=100,
        )

        file_reference_details = extract_file_reference_details(
            accession_id,
            f"{study.uuid}",
            f"{dataset.uuid}",
            file_references,
            include_annotation_details,
        )
        convertible_file_references.extend(file_reference_details)

    convertible_file_references = sorted(
        convertible_file_references,
        key=lambda fr: (fr["size_in_bytes"], fr["name"]),
        reverse=True,
    )
    return convertible_file_references


def write_convertible_file_references_for_accession_id(
    accession_id: str,
    output_path: Path,
    api_target: ApiTarget,
    max_items: int = 5,
    append: bool = True,
    check_image_creation_prerequisites: bool = True,
) -> int:
    """
    Write details of file references proposed for conversion to file
    """

    # Ensure we can write out the results before going through file references
    output_path_suffix = output_path.suffix.lower()
    if output_path_suffix == ".tsv":
        write_file_reference_details_func = write_file_reference_details_to_tsv
    elif output_path_suffix == ".yaml" or output_path_suffix == ".yml":
        write_file_reference_details_func = write_file_reference_details_to_yaml
    else:
        raise Exception(
            f"Proposals writer not implemented for suffix {output_path_suffix}"
        )

    convertible_file_references = get_convertible_file_references(
        accession_id, api_target, check_image_creation_prerequisites
    )

    n_proposal_candidates = len(convertible_file_references)
    indicies_to_select = select_indicies(n_proposal_candidates, max_items)
    file_reference_details = [
        convertible_file_references[i] for i in indicies_to_select
    ]

    write_file_reference_details_func(
        file_reference_details,
        output_path,
        append,
    )

    return len(indicies_to_select)


def write_convertible_source_annotation_file_refs_for_acc_id(
    accession_id: str,
    output_path: Path,
    api_target: ApiTarget,
    max_items: int = 5,
    append: bool = True,
    check_image_creation_prerequisites: bool = True,
) -> tuple[int, int]:
    """
    Write details of file references proposed for conversion to file
    """

    # Ensure we can write out the results before going through file references
    output_path_suffix = output_path.suffix.lower()
    if output_path_suffix == ".tsv":
        write_file_reference_details_func = write_file_reference_details_to_tsv
    elif output_path_suffix == ".yaml" or output_path_suffix == ".yml":
        write_file_reference_details_func = write_file_reference_details_to_yaml
    else:
        raise Exception(
            f"Proposals writer not implemented for suffix {output_path_suffix}"
        )

    convertible_file_references = get_convertible_file_references(
        accession_id,
        api_target,
        check_image_creation_prerequisites,
        include_annotation_details=True,
    )

    # index annotation images by their corresponding source images
    index = {}
    for fr in convertible_file_references:
        if "source_image" in fr and "source_image_uuid" in fr:
            source_image_path = fr["source_image"]
            source_image_details = next(
                (
                    f
                    for f in convertible_file_references
                    if f["name"] == source_image_path
                ),
                None,
            )
            if not source_image_details:
                continue

            if source_image_path not in index:
                index[source_image_path] = {
                    "source_file_reference": source_image_details,
                    "annotation_file_references": [fr],
                }
            else:
                index[source_image_path]["annotation_file_references"].append(fr)

    n_proposal_candidates = len(index)
    indicies_to_select = select_indicies(n_proposal_candidates, max_items)
    keys = list(index.keys())
    keys_to_select = [keys[i] for i in indicies_to_select]
    file_reference_details = []
    n_annotations = 0
    for key in keys_to_select:
        file_reference_details.append(index[key]["source_file_reference"])
        file_reference_details.extend(index[key]["annotation_file_references"])
        n_annotations += len(index[key]["annotation_file_references"])

    write_file_reference_details_func(
        file_reference_details,
        output_path,
        append,
    )

    n_source_images = len(indicies_to_select)
    return (n_source_images, n_annotations)


def write_file_reference_details_to_tsv(
    file_reference_details: List[Dict], output_path: Path, append_flag: bool = False
):
    if append_flag:
        open_text_mode = "a"
    else:
        open_text_mode = "w"

    lines = [
        "\t".join(
            [
                f["accession_id"],
                f"{f['study_uuid']}",
                f"{f['dataset_uuid']}",
                f["name"],
                f"{f['file_reference_uuid']}",
                f"{f['size_in_bytes']}",
                f["size_human_readable"],
            ]
        )
        for f in file_reference_details
    ]
    with output_path.open(open_text_mode) as fid:
        # If we are at start of file write header.
        if fid.tell() == 0:
            fid.writelines(
                "\t".join(
                    [
                        "accession_id",
                        "study_uuid",
                        "dataset_uuid",
                        "name",
                        "file_reference_uuid",
                        "size_in_bytes",
                        "size_human_readable",
                    ]
                )
            )
            fid.writelines("\n")
        fid.writelines("\n".join(lines))
        # Write a new line so next append starts on next line
        fid.writelines("\n")
    return


def write_file_reference_details_to_yaml(
    file_reference_details: List[Dict], output_path: Path, append_flag: bool = False
):
    yaml = YAML()
    yaml.default_flow_style = False
    if append_flag and output_path.is_file():
        file_reference_details_from_file = read_proposals_from_yaml(output_path)
        file_reference_details_from_file.extend(file_reference_details)
        yaml.dump(file_reference_details_from_file, output_path)
    else:
        yaml.dump(file_reference_details, output_path)
    return


def read_proposals(proposal_path: Path) -> List[Dict]:
    """Read proposals from a tab-separated file

    Returns a list of dicts containing file reference info
    """
    proposal_path_suffix = proposal_path.suffix.lower()
    if proposal_path_suffix == ".tsv":
        proposals = read_proposals_from_tsv(proposal_path)
    elif proposal_path_suffix == ".yaml" or proposal_path_suffix == ".yml":
        proposals = read_proposals_from_yaml(proposal_path)
    else:
        raise Exception(
            f"Proposals reader not implemented for suffix {proposal_path_suffix}"
        )

    return proposals


def read_proposals_from_tsv(proposal_path: Path) -> List[Dict]:
    proposals = []
    with proposal_path.open("r", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")  # Uses first line as field names
        for row in reader:
            if not row["accession_id"]:  # Skip empty lines
                continue
            row["size_in_bytes"] = int(row["size_in_bytes"])  # Convert size to int
            proposals.append(row)

    return proposals


def read_proposals_from_yaml(proposal_path: Path) -> List[Dict]:
    yaml = YAML(typ="safe")
    proposals = yaml.load(proposal_path)
    return proposals


def extract_file_reference_details(
    accession_id: str,
    study_uuid: str,
    dataset_uuid: str,
    file_references: list[bia_data_model.FileReference],
    include_annotation_details,
) -> list[dict]:
    file_reference_details = []

    for fr in file_references:
        if not in_bioformats_single_file_formats_list(fr.file_path):
            continue

        fr_details = {
            "accession_id": accession_id,
            "study_uuid": study_uuid,
            "dataset_uuid": dataset_uuid,
            "name": fr.file_path,
            "file_reference_uuid": fr.uuid,
            "size_in_bytes": fr.size_in_bytes,
            "size_human_readable": sizeof_fmt(fr.size_in_bytes),
        }

        # TODO: Should we just include these by default if they exist?
        if include_annotation_details:
            source_image_uuid = get_value_from_attribute_list(
                fr.additional_metadata, "source_image_uuid"
            )
            if source_image_uuid:
                fr_details["source_image_uuid"] = source_image_uuid

                attributes = get_value_from_attribute_list(
                    fr.additional_metadata,
                    "attributes_from_biostudies.File",
                    attribute_value_name="attributes",
                )
                if attributes:
                    source_image = attributes.get("source_image")
                    if source_image:
                        fr_details["source_image"] = source_image

        file_reference_details.append(fr_details)

    return file_reference_details
