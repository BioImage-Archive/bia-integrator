from pathlib import Path
import pytest
from ro_crate_ingest.biostudies_to_ro_crate.entity_conversion.file_list import (
    combine_file_lists,
)


@pytest.fixture
def files_to_combine(tmp_path) -> dict[str, Path]:
    file_list_paths = {}
    for i in range(1, 3):
        file_path = tmp_path / f"file_list_{i}.tsv"
        data = "\t".join(
            [
                "path",
                "size",
                "type",
                f"metadata_header{i}_1",
                f"metadata_header{i}_2",
                f"metadata_header{i}_3",
            ]
        )
        for row in range(2, 5):
            data += "\n" + "\t".join(
                [
                    f"file_{i}_{row}.png",
                    f"{row*100}",
                    "file",
                    f"metadata_value{i}_1_{row}",
                    f"metadata_value{i}_2_{row}",
                    f"metadata_value{i}_3_{row}",
                ]
            )
        file_path.write_text(data)
        file_list_paths[f"dataset_{i}"] = file_path
    return file_list_paths


@pytest.fixture
def expected_combined_file_list() -> str:
    data = [
        "\t".join(
            [
                "path",
                "size",
                "type",
                "dataset",
                f"metadata_header1_1",
                f"metadata_header1_2",
                f"metadata_header1_3",
                f"metadata_header2_1",
                f"metadata_header2_2",
                f"metadata_header2_3",
            ]
        ),
    ]

    for row in range(2, 5):
        data.append(
            "\t".join(
                [
                    f"file_1_{row}.png",
                    f"{row*100}",
                    "file",
                    "dataset_1",
                    f"metadata_value1_1_{row}",
                    f"metadata_value1_2_{row}",
                    f"metadata_value1_3_{row}",
                    "",
                    "",
                    "",
                ]
            )
        )

    for row in range(2, 5):
        data.append(
            "\t".join(
                [
                    f"file_2_{row}.png",
                    f"{row*100}",
                    "file",
                    "dataset_2",
                    "",
                    "",
                    "",
                    f"metadata_value2_1_{row}",
                    f"metadata_value2_2_{row}",
                    f"metadata_value2_3_{row}",
                ]
            )
        )
    return data


def test_combine_biostudies_filelists(
    tmp_path,
    files_to_combine: dict[str, Path],
    expected_combined_file_list: list[str],
):

    output_path = tmp_path / "combined_file_list.tsv"

    # Call the function to combine file lists
    combine_file_lists(files_to_combine, output_path.parent, output_path.name)

    # Read the output file and verify its contents
    combined_contents = output_path.read_text().strip().split("\n")

    assert combined_contents == expected_combined_file_list
