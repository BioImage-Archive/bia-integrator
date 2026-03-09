"""Unit tests for multi-plane conversion functions in bia_converter.convert.

Tests find_file_references_with_explicit_indices, find_file_references_matching_template,
and fileref_map_to_bfconvert_pattern without requiring API, Docker, or bioformats2raw.
"""

from bia_integrator_api.models import FileReference, Attribute

from bia_converter.convert import (
    find_file_references_with_explicit_indices,
    find_file_references_matching_template,
    fileref_map_to_bfconvert_pattern,
)


def make_file_reference(uuid, file_path, z_index=None, t_index=None, c_index=None):
    """Construct a FileReference with optional z/t/c index metadata."""
    attrs_value = {"file_path": file_path}
    if z_index is not None:
        attrs_value["z_index"] = z_index
    if t_index is not None:
        attrs_value["t_index"] = t_index
    if c_index is not None:
        attrs_value["c_index"] = c_index

    additional_metadata = [
        Attribute.model_validate(
            {
                "provenance": "bia_ingest",
                "name": "attributes_from_file_list",
                "value": attrs_value,
            }
        )
    ]

    return FileReference(
        uuid=uuid,
        version=0,
        file_path=file_path,
        format=".tif",
        size_in_bytes=100,
        uri=f"https://example.com/{file_path}",
        submission_dataset_uuid="test-dataset-uuid",
        object_creator="bia_ingest",
        additional_metadata=additional_metadata,
    )


# --- Tests for find_file_references_with_explicit_indices ---


class TestFindFileReferencesWithExplicitIndices:
    def test_z_index_only(self):
        filerefs = [
            make_file_reference("fr-0", "img_0.tif", z_index=0),
            make_file_reference("fr-1", "img_1.tif", z_index=1),
            make_file_reference("fr-2", "img_2.tif", z_index=2),
        ]
        selected, coord_map = find_file_references_with_explicit_indices(filerefs)

        assert len(selected) == 3
        assert coord_map["fr-0"] == (0, 0, 0)
        assert coord_map["fr-1"] == (0, 0, 1)
        assert coord_map["fr-2"] == (0, 0, 2)

    def test_c_index_only(self):
        filerefs = [
            make_file_reference("fr-0", "ch0.tif", c_index=0),
            make_file_reference("fr-1", "ch1.tif", c_index=1),
            make_file_reference("fr-2", "ch2.tif", c_index=2),
        ]
        selected, coord_map = find_file_references_with_explicit_indices(filerefs)

        assert len(selected) == 3
        assert coord_map["fr-0"] == (0, 0, 0)
        assert coord_map["fr-1"] == (0, 1, 0)
        assert coord_map["fr-2"] == (0, 2, 0)

    def test_all_three_indices(self):
        filerefs = [
            make_file_reference("fr-0", "img_0.tif", z_index=0, t_index=1, c_index=2),
            make_file_reference("fr-1", "img_1.tif", z_index=3, t_index=4, c_index=5),
        ]
        selected, coord_map = find_file_references_with_explicit_indices(filerefs)

        assert len(selected) == 2
        assert coord_map["fr-0"] == (1, 2, 0)
        assert coord_map["fr-1"] == (4, 5, 3)

    def test_no_indices(self):
        filerefs = [
            make_file_reference("fr-0", "img_0.tif"),
            make_file_reference("fr-1", "img_1.tif"),
        ]
        selected, coord_map = find_file_references_with_explicit_indices(filerefs)

        assert selected == []
        assert coord_map == {}

    def test_mixed_indices_returns_empty(self):
        """If any fileref lacks indices, the function returns empty."""
        filerefs = [
            make_file_reference("fr-0", "img_0.tif", z_index=0),
            make_file_reference("fr-1", "img_1.tif"),  # no indices
        ]
        selected, coord_map = find_file_references_with_explicit_indices(filerefs)

        assert selected == []
        assert coord_map == {}

    def test_string_index_values(self):
        """Indices from TSV parsing may be strings; should be converted to int."""
        filerefs = [
            make_file_reference("fr-0", "img_0.tif", z_index="5"),
            make_file_reference("fr-1", "img_1.tif", z_index="10"),
        ]
        selected, coord_map = find_file_references_with_explicit_indices(filerefs)

        assert len(selected) == 2
        assert coord_map["fr-0"] == (0, 0, 5)
        assert coord_map["fr-1"] == (0, 0, 10)


# --- Tests for find_file_references_matching_template ---


class TestFindFileReferencesMatchingTemplate:
    def test_z_only_template(self):
        filerefs = [
            make_file_reference("fr-0", "img_Z0.tif", z_index=0),
            make_file_reference("fr-1", "img_Z1.tif", z_index=1),
            make_file_reference("fr-2", "img_Z2.tif", z_index=2),
        ]
        template = "img_Z{z:d}.tif"
        selected, coord_map = find_file_references_matching_template(filerefs, template)

        assert len(selected) == 3
        assert coord_map["fr-0"] == (0, 0, 0)
        assert coord_map["fr-1"] == (0, 0, 1)
        assert coord_map["fr-2"] == (0, 0, 2)

    def test_full_tcz_template(self):
        filerefs = [
            make_file_reference("fr-0", "img_t2_c3_z10.tif"),
            make_file_reference("fr-1", "img_t0_c1_z5.tif"),
        ]
        template = "img_t{t:d}_c{c:d}_z{z:d}.tif"
        selected, coord_map = find_file_references_matching_template(filerefs, template)

        assert len(selected) == 2
        assert coord_map["fr-0"] == (2, 3, 10)
        assert coord_map["fr-1"] == (0, 1, 5)

    def test_partial_match(self):
        filerefs = [
            make_file_reference("fr-0", "img_Z0.tif"),
            make_file_reference("fr-1", "other_file.png"),
            make_file_reference("fr-2", "img_Z1.tif"),
        ]
        template = "img_Z{z:d}.tif"
        selected, coord_map = find_file_references_matching_template(filerefs, template)

        assert len(selected) == 2
        assert set(fr.uuid for fr in selected) == {"fr-0", "fr-2"}
        assert "fr-1" not in coord_map


# --- Tests for fileref_map_to_bfconvert_pattern ---


class TestFilerefMapToBfconvertPattern:
    def test_z_only_range(self):
        fileref_map = {f"fr-{i}": (0, 0, i) for i in range(396)}
        pattern = fileref_map_to_bfconvert_pattern(fileref_map, ".tif")

        assert pattern == "T<0000-0000>_C<0000-0000>_Z<0000-0395>.tif"

    def test_multi_dimensional(self):
        fileref_map = {
            "fr-0": (0, 0, 0),
            "fr-1": (0, 0, 1),
            "fr-2": (0, 1, 0),
            "fr-3": (0, 1, 1),
            "fr-4": (1, 0, 0),
            "fr-5": (1, 0, 1),
            "fr-6": (1, 1, 0),
            "fr-7": (1, 1, 1),
        }
        pattern = fileref_map_to_bfconvert_pattern(fileref_map, ".tif")

        assert pattern == "T<0000-0001>_C<0000-0001>_Z<0000-0001>.tif"
