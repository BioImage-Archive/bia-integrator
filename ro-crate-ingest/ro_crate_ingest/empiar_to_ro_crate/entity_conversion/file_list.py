import pandas as pd
import logging
import parse
import json

from dataclasses import dataclass
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import Entry
from ro_crate_ingest.empiar_to_ro_crate.empiar.file_api import get_files, EMPIARFile
from pathlib import Path
from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.models.linked_data.ontology_terms import BIA, SCHEMA
from rdflib import RDF
from ro_crate_ingest.save_utils import write_filelist
from typing import Optional
from urllib.parse import quote

logger = logging.getLogger("__main__." + __name__)

# Avoid debug logging for every attempted parse.
requests_logger = logging.getLogger("parse")
requests_logger.setLevel(logging.INFO)


@dataclass
class PatternMatch:
    file_pattern: str
    dataset_id: str
    object_type: str | None
    yaml_object: dict | None
    match_count: int = 0


def create_file_list(
    output_ro_crate_path: Path,
    empiar_api_entry: Entry,
    datasets_map: dict[str, ro_crate_models.Dataset],
    yaml_file: dict | None = None,
    accession_id: str | None = None,
) -> list[
    ro_crate_models.FileList | ro_crate_models.TableSchema | ro_crate_models.Column
]:
    """
    Unlike biostudies, all EMPIAR file lists have the same schema.

    If part of the proposal-based route:
        will create a separate list for 'unassigned' files that do not match any dataset if there are any.
        This is saved as unassigned_files.json in the RO-Crate directory (but not referenced as part of the RO-Crate).
    But if part of minimal route, unassigned files are not separated, and dealt with later.

    And note: if proposal-based, a yaml_file proposal is expected, and if minimal, the accession_id must be supplied.
    """
    if yaml_file is None and accession_id is None:
        raise ValueError("Either yaml_file or accession_id must be provided")

    columns = get_column_list()
    schema = get_schema(columns)

    file_df = create_base_dataframe_from_file_paths(
        yaml_file["accession_id"] if yaml_file else accession_id
    )

    if yaml_file:
        path_pattern_objects = get_file_patterns_matches_and_objects(
            yaml_file, empiar_api_entry, datasets_map
        )

        file_list_df = expand_dataframe_metadata(path_pattern_objects, file_df)

        file_list_df = separate_and_report_unassigned_files(
            file_list_df, output_ro_crate_path
        )
    elif accession_id:
        file_list_df = expand_dataframe_metadata([], file_df)
        file_list_df = assign_datasets_in_minimal_rocrate(
            file_list_df, empiar_api_entry, datasets_map
        )

    ro_crate_objects: list = [schema]
    ro_crate_objects.extend(columns)

    file_list_id = "file_list.tsv"
    ro_crate_objects.append(get_ro_crate_filelist(file_list_id, schema))

    write_filelist(output_ro_crate_path, file_list_id, file_list_df)

    return ro_crate_objects


# TODO: can refactor in proposal-based route to use this function where appropriate
def _rate_dataset_specificity(data_directories: list[str]) -> int:
    """
    Return a specificity score for a dataset, defined as the maximum
    number of '/' separators across its data_directories. Used to break ties
    when multiple dataset blocks claim the same file: the deeper directory wins.
    """
    return max((d.count("/") for d in data_directories), default=0)


def _find_dataset_for_file(
    file_path: str, imageset_to_dataset_id: dict[str, str]
) -> Optional[str]:
    matching_datasets = [
        (dataset_id, dir_name)
        for dir_name, dataset_id in imageset_to_dataset_id.items()
        if dir_name in file_path
    ]
    if not matching_datasets:
        return None
    return max(matching_datasets, key=lambda x: _rate_dataset_specificity([x[1]]))[0]


def assign_datasets_in_minimal_rocrate(
    file_list_df: pd.DataFrame,
    empiar_api_entry: Entry,
    datasets_map: dict[str, ro_crate_models.Dataset],
) -> pd.DataFrame:
    """
    In the minimal ro-crate route, we don't have a yaml proposal to guide the assignment of files to datasets.

    This function will look for dataset directory names in the file paths, and assign files to datasets accordingly.
    If a file path contains multiple dataset directory names, the most specific (longest) match will be used.
    If no dataset directory names are found in the file path, the dataset will be left unassigned (NaN).
    """
    imageset_to_dataset_id = {
        imageset.directory: dataset.id
        for imageset in empiar_api_entry.imagesets
        for dataset in datasets_map.values()
        if dataset.name == imageset.name
    }
    file_list_df["dataset"] = file_list_df["file_path"].apply(
        _find_dataset_for_file, args=(imageset_to_dataset_id,)
    )

    return file_list_df


def create_base_dataframe_from_file_paths(accession_id: str):
    files: list[EMPIARFile] = get_files(accession_id)
    file_df: pd.DataFrame = pd.DataFrame(
        files,
    ).map(lambda x: x[1])
    file_df.columns = ["file_path", "size_in_bytes"]
    return file_df


def expand_dataframe_metadata(
    path_pattern_objects: list[PatternMatch],
    file_df: pd.DataFrame,
):

    file_list_df = file_df.apply(
        expand_row_metadata,
        args=(path_pattern_objects, file_df["file_path"].to_list()),
        axis=1,
    )

    for pattern_match in path_pattern_objects:
        if pattern_match.match_count == 0 and pattern_match.yaml_object:
            logger.warning(f"Pattern: {pattern_match.file_pattern} matched zero files.")

    return file_list_df


def get_file_patterns_matches_and_objects(
    yaml_file, empiar_api_entry: Entry, datasets_map: dict[str, ro_crate_models.Dataset]
) -> list[PatternMatch]:
    """
    yaml containts the assigned image, annotation & file assocaiation file patterns
    empiar api entry has folder paths

    returns a list of PatternMatch objects, containing:
        file pattern which can be used to match file paths
        dataset id
        (optional) object type,
        (optional) object from yaml
    """

    image_to_dataset_map = []
    annotation_data_to_dataset_map = []
    file_pattern_to_dataset_map = []
    images_set_path_to_dataset_map = []

    imageset_to_path = {
        imageset.name: imageset.directory for imageset in empiar_api_entry.imagesets
    }

    title_to_dataset_id = {
        imageset_title: dataset.id for imageset_title, dataset in datasets_map.items()
    }

    for dataset in yaml_file["datasets"]:
        dataset_id = title_to_dataset_id[dataset["title"]]
        for image in dataset.get("assigned_images", ()):
            image_to_dataset_map.append(
                PatternMatch(
                    f"data/{image["file_pattern"]}",
                    dataset_id,
                    "http://bia/Image",
                    image,
                )
            )
        for annotation in dataset.get("assigned_annotations", ()):
            annotation_data_to_dataset_map.append(
                PatternMatch(
                    f"data/{annotation["file_pattern"]}",
                    dataset_id,
                    "http://bia/AnnotationData",
                    annotation,
                )
            )
        for additional_file in dataset.get("additional_files", ()):
            file_pattern_to_dataset_map.append(
                PatternMatch(
                    f"data/{additional_file["file_pattern"]}",
                    dataset_id,
                    None,
                    additional_file,
                )
            )
        images_set_path_to_dataset_map.append(
            PatternMatch(
                f"{imageset_to_path[dataset["title"]]}/{{rest}}",
                dataset_id,
                None,
                None,
            )
        )

    # Sort paths by specificity to deal with nested imagesets
    images_set_path_to_dataset_map = sort_imageset_paths_by_specificity(
        images_set_path_to_dataset_map
    )

    # Order matters for preferential matching: image_sets should be last, and file_patterns should be after images & annotation.
    path_maps = (
        image_to_dataset_map
        + annotation_data_to_dataset_map
        + file_pattern_to_dataset_map
        + images_set_path_to_dataset_map
    )

    return path_maps


def sort_imageset_paths_by_specificity(
    pattern_matches: list[PatternMatch],
) -> list[PatternMatch]:

    return sorted(
        pattern_matches, key=lambda pm: pm.file_pattern.count("/"), reverse=True
    )


def expand_row_metadata(
    row: pd.Series, path_maps: list[PatternMatch], all_file_paths: list[Path]
) -> pd.Series:
    file_path: Path = row["file_path"]

    path = file_path.as_posix()

    output_row = {
        "file_path": str(file_path),
        "size_in_bytes": int(row["size_in_bytes"]),
        "dataset": None,
        "type": None,
        "label": None,
        "associated_source_image": None,
        "associated_subject": None,
        "associated_annotation_method": None,
        "associated_protocol": None,
    }

    for pattern_match in path_maps:
        if parse.parse(pattern_match.file_pattern, path):
            update_row(
                output_row,
                pattern_match.yaml_object,
                pattern_match.object_type,
                pattern_match.dataset_id,
                all_file_paths,
            )
            pattern_match.match_count += 1
            break

    if output_row["dataset"] is None:
        logger.debug(f"Unassigned file detected: {file_path}")

    return pd.Series(output_row)


def update_row(
    output_row: dict,
    yaml_object: Optional[dict],
    row_type: Optional[str],
    dataset_id: str,
    all_file_paths: list[Path],
):
    output_row["type"] = row_type
    output_row["dataset"] = dataset_id

    if yaml_object:
        if label := yaml_object.get("label", None):
            output_row["label"] = label
        elif label_prefix := yaml_object.get("label_prefix", None):
            label_parts = parse_file_path_for_label(
                output_row["file_path"], yaml_object.get("file_pattern", "")
            )
            if label_parts is not None:
                output_row["label"] = f"{label_prefix}_{label_parts}"

        specimen_title = yaml_object.get("specimen_title", None)
        output_row["associated_subject"] = (
            f"#{quote(specimen_title)}" if specimen_title else None
        )

        annotation_method_title = yaml_object.get("annotation_method_title", None)
        output_row["associated_annotation_method"] = (
            [f"#{quote(title)}" for title in annotation_method_title]
            if isinstance(annotation_method_title, list)
            else (
                f"#{quote(annotation_method_title)}"
                if annotation_method_title
                else None
            )
        )

        protocol_title = yaml_object.get("protocol_title", None)
        output_row["associated_protocol"] = (
            [f"#{quote(title)}" for title in protocol_title]
            if isinstance(protocol_title, list)
            else f"#{quote(protocol_title)}" if protocol_title else None
        )

        if input_label := yaml_object.get("input_label", None):
            output_row["associated_source_image"] = input_label
        elif input_label_prefix := yaml_object.get("input_label_prefix", None):
            matching_label_parts = find_matching_input_label_parts(
                all_file_paths, yaml_object.get("input_file_pattern", "")
            )
            output_row["associated_source_image"] = create_input_labels(
                input_label_prefix, matching_label_parts
            )


def parse_file_path_for_label(file_path: str, file_pattern: str) -> str | None:

    result = parse.parse(f"data/{file_pattern}", file_path)
    if result is not None:
        label_parts = [str(part) for part in result.fixed]
        return "_".join(label_parts)

    return result


def find_matching_input_label_parts(
    file_paths: list[Path], input_image_pattern: str
) -> list[str]:

    matches = []
    for path in file_paths:
        matching_parts = parse_file_path_for_label(str(path), input_image_pattern)
        if matching_parts is not None:
            matches.append(matching_parts)

    if len(matches) == 0:
        raise ValueError(f"No file parts found to match input image pattern")

    return sorted(matches)


def create_input_labels(label_prefix: str, file_parts: list[str]) -> list[str]:

    labels = [f"{label_prefix}_{part}" for part in file_parts]
    return labels


def separate_and_report_unassigned_files(
    file_list_df: pd.DataFrame,
    output_ro_crate_path: Path,
) -> pd.DataFrame:

    unassigned_entries = file_list_df["dataset"].isna()
    unassigned_files_df = file_list_df[unassigned_entries]
    assigned_files_df = file_list_df[~unassigned_entries]

    if len(unassigned_files_df) == 0:
        logger.info("All files successfully assigned to datasets.")
        return assigned_files_df

    unassigned_file_paths = unassigned_files_df["file_path"].tolist()
    logger.warning(f"Total unassigned files: {len(unassigned_file_paths)}")

    unassigned_json_path = output_ro_crate_path / "unassigned_files.json"
    unassigned_data = {"files": unassigned_file_paths}

    with open(unassigned_json_path, "w") as f:
        json.dump(unassigned_data, f, indent=2)

    logger.info(
        f"Wrote {len(unassigned_file_paths)} unassigned file(s) to {unassigned_json_path}"
    )

    return assigned_files_df


def get_ro_crate_filelist(
    filelist_id: str, schema: ro_crate_models.TableSchema
) -> ro_crate_models.FileList:

    filelist_dict = {
        "@id": filelist_id,
        "@type": ["File", "bia:FileList", "csvw:Table"],
        "tableSchema": {"@id": schema.id},
    }

    return ro_crate_models.FileList(**filelist_dict)


def get_schema(
    columns_for_schema: list[ro_crate_models.Column],
) -> ro_crate_models.TableSchema:

    tableSchema = {
        "@id": "_:ts0",
        "@type": ["csvw:Schema"],
        "column": [{"@id": column.id} for column in columns_for_schema],
    }
    schema = ro_crate_models.TableSchema(**tableSchema)
    return schema


def get_column_list() -> list[ro_crate_models.Column]:

    columns_properties = {
        "file_path": BIA.filePath,
        "size_in_bytes": BIA.sizeInBytes,
        "dataset": SCHEMA.isPartOf,
        "type": RDF.type,
        "label": SCHEMA.name,
        "associated_source_image": BIA.associatedSourceImage,
        "associated_subject": BIA.associatedSubject,
        "associated_annotation_method": BIA.associatedAnnotationMethod,
        "associated_protocol": BIA.associatedProtocol,
    }

    id_no = 0
    columns = []

    for column_header, property in columns_properties.items():
        model_dict = {
            "@id": f"_:col{id_no}",
            "@type": ["csvw:Column"],
            "columnName": column_header,
        }
        if property:
            model_dict["propertyUrl"] = str(property)
        columns.append(ro_crate_models.Column(**model_dict))
        id_no += 1

    return columns
