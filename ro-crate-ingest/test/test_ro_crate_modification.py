import json
import shutil
import traceback
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import pytest
from bia_ro_crate.core.file_list import FileList
from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.models.linked_data.ontology_terms import BIA
from rdflib import RDF
from typer.testing import CliRunner

from ro_crate_ingest.cli import ro_crate_ingest
from ro_crate_ingest.ro_crate_modification.enrichment.assignments import (
    ResultAssignmentContext,
    _apply_result_assignment,
)
from ro_crate_ingest.ro_crate_modification.enrichment.file_list_utils import (
    file_list_association_value,
    get_or_add_label_column_id,
)
from ro_crate_ingest.ro_crate_modification.enrichment.specimens import (
    SpecimenTrack,
    _generate_labels,
    _write_associated_protocol,
    _write_source_image_labels,
)
from ro_crate_ingest.ro_crate_modification.modification_config import (
    DatasetModificationConfig,
    SpecimenTrackAssignmentConfig,
)

runner = CliRunner()


def title_to_id(title: str) -> str:
    return f"#{quote(title)}"


def _fixture_root() -> Path:
    return Path(__file__).parent / "ro_crate_modification"


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([], None),
        (["#Protocol%20one"], "#Protocol%20one"),
        (
            ["#Protocol%20one", "#Protocol%20two"],
            "['#Protocol%20one', '#Protocol%20two']",
        ),
    ],
)
def test_file_list_association_value(values, expected):
    assert file_list_association_value(values) == expected


def test_result_assignment_warns_before_overwriting_type(caplog):
    schema = {
        "_:col0": ro_crate_models.Column(
            **{
                "@id": "_:col0",
                "@type": ["csvw:Column"],
                "columnName": "file_path",
                "propertyUrl": str(BIA.filePath),
            }
        ),
        "_:col1": ro_crate_models.Column(
            **{
                "@id": "_:col1",
                "@type": ["csvw:Column"],
                "columnName": "dataset",
                "propertyUrl": "http://schema.org/isPartOf",
            }
        ),
        "_:col2": ro_crate_models.Column(
            **{
                "@id": "_:col2",
                "@type": ["csvw:Column"],
                "columnName": "type",
                "propertyUrl": str(RDF.type),
            }
        ),
    }
    file_list = FileList(
        schema=schema,
        data=pd.DataFrame(
            {
                "file_path": ["data/cell_001_mask.csv"],
                "dataset": ["#Fluorescence%20microscopy%20images"],
                "type": ["http://bia/Image"],
            }
        ),
    )

    context = ResultAssignmentContext(
        file_list=file_list,
        dataset_name="Fluorescence microscopy images",
        dataset_id="#Fluorescence%20microscopy%20images",
        dataset_col_id="_:col1",
        path_col_id="_:col0",
        type_col_id="_:col2",
    )

    count = _apply_result_assignment(
        context,
        assignment_name="annotation assignment",
        patterns=["**/*.csv"],
        result_type="http://bia/AnnotationData",
    )

    assert count == 1
    assert file_list.data.at[0, "_:col2"] == "http://bia/AnnotationData"
    assert "overwriting existing type" in caplog.text


def test_get_or_add_label_column_id_creates_missing_column():
    schema = {
        "_:col0": ro_crate_models.Column(
            **{
                "@id": "_:col0",
                "@type": ["csvw:Column"],
                "columnName": "file_path",
                "propertyUrl": str(BIA.filePath),
            }
        ),
        "_:col1": ro_crate_models.Column(
            **{
                "@id": "_:col1",
                "@type": ["csvw:Column"],
                "columnName": "dataset",
                "propertyUrl": "http://schema.org/isPartOf",
            }
        ),
    }
    file_list = FileList(
        schema=schema,
        data=pd.DataFrame(
            {
                "file_path": ["data/cell_001_mask.csv"],
                "dataset": ["#Fluorescence%20microscopy%20images"],
            }
        ),
    )

    col_id = get_or_add_label_column_id(file_list)

    assert file_list.schema[col_id].columnName == "label"
    assert file_list.schema[col_id].propertyUrl == "http://schema.org/name"
    assert col_id in file_list.data.columns


def test_segmentation_source_image_type_can_use_denoised_tomogram():
    schema = {
        "_:col0": ro_crate_models.Column(
            **{
                "@id": "_:col0",
                "@type": ["csvw:Column"],
                "columnName": "file_path",
                "propertyUrl": str(BIA.filePath),
            }
        )
    }
    file_list = FileList(
        schema=schema,
        data=pd.DataFrame(
            {
                "file_path": [
                    "data/tomo/tomo_001.mrc",
                    "data/tomo/tomo_001_denoised.mrc",
                    "data/tomo/tomo_001_segmentation.mrcseg",
                ]
            }
        ),
    )
    track = SpecimenTrack(
        specimen_id="001",
        tomogram=Path("data/tomo/tomo_001.mrc"),
        denoised_tomogram=Path("data/tomo/tomo_001_denoised.mrc"),
        segmentations=[Path("data/tomo/tomo_001_segmentation.mrcseg")],
        dataset_for_path={
            "data/tomo/tomo_001_segmentation.mrcseg": "Reconstructed tomograms"
        },
    )
    dataset_config = DatasetModificationConfig(
        name="Reconstructed tomograms",
        specimen_tracks=SpecimenTrackAssignmentConfig(
            source_image_types={"segmentation": "denoised_tomogram"}
        ),
    )

    _write_source_image_labels(
        file_list=file_list,
        tracks=[track],
        path_to_label=_generate_labels([track]),
        dataset_configs=[dataset_config],
    )

    source_col = file_list.get_column_id_by_property(str(BIA.associatedSourceImage))
    seg_row = file_list.data[
        file_list.data["_:col0"] == "data/tomo/tomo_001_segmentation.mrcseg"
    ]
    assert seg_row.iloc[0][source_col] == "Specimen_001 denoised_tomogram"


def test_missing_configured_segmentation_source_logs_warning(caplog):
    schema = {
        "_:col0": ro_crate_models.Column(
            **{
                "@id": "_:col0",
                "@type": ["csvw:Column"],
                "columnName": "file_path",
                "propertyUrl": str(BIA.filePath),
            }
        )
    }
    file_list = FileList(
        schema=schema,
        data=pd.DataFrame(
            {
                "file_path": [
                    "data/tomo/tomo_001.mrc",
                    "data/tomo/tomo_001_segmentation.mrcseg",
                ]
            }
        ),
    )
    track = SpecimenTrack(
        specimen_id="001",
        tomogram=Path("data/tomo/tomo_001.mrc"),
        segmentations=[Path("data/tomo/tomo_001_segmentation.mrcseg")],
        dataset_for_path={
            "data/tomo/tomo_001_segmentation.mrcseg": "Reconstructed tomograms"
        },
    )
    dataset_config = DatasetModificationConfig(
        name="Reconstructed tomograms",
        specimen_tracks=SpecimenTrackAssignmentConfig(
            source_image_types={"segmentation": "denoised_tomogram"}
        ),
    )

    _write_source_image_labels(
        file_list=file_list,
        tracks=[track],
        path_to_label=_generate_labels([track]),
        dataset_configs=[dataset_config],
    )

    source_col = file_list.get_column_id_by_property(str(BIA.associatedSourceImage))
    seg_row = file_list.data[
        file_list.data["_:col0"] == "data/tomo/tomo_001_segmentation.mrcseg"
    ]
    assert seg_row.iloc[0][source_col] == "Specimen_001 tomogram"
    assert (
        "configured segmentation source 'denoised_tomogram' was not available"
        in caplog.text
    )


def test_segmentation_source_image_falls_back_to_denoised_tomogram():
    schema = {
        "_:col0": ro_crate_models.Column(
            **{
                "@id": "_:col0",
                "@type": ["csvw:Column"],
                "columnName": "file_path",
                "propertyUrl": str(BIA.filePath),
            }
        )
    }
    file_list = FileList(
        schema=schema,
        data=pd.DataFrame(
            {
                "file_path": [
                    "data/tomo/tomo_001_denoised.mrc",
                    "data/tomo/tomo_001_segmentation.mrcseg",
                ]
            }
        ),
    )
    track = SpecimenTrack(
        specimen_id="001",
        denoised_tomogram=Path("data/tomo/tomo_001_denoised.mrc"),
        segmentations=[Path("data/tomo/tomo_001_segmentation.mrcseg")],
        dataset_for_path={
            "data/tomo/tomo_001_segmentation.mrcseg": "Reconstructed tomograms"
        },
    )
    dataset_config = DatasetModificationConfig(
        name="Reconstructed tomograms",
        specimen_tracks=SpecimenTrackAssignmentConfig(),
    )

    _write_source_image_labels(
        file_list=file_list,
        tracks=[track],
        path_to_label=_generate_labels([track]),
        dataset_configs=[dataset_config],
    )

    source_col = file_list.get_column_id_by_property(str(BIA.associatedSourceImage))
    seg_row = file_list.data[
        file_list.data["_:col0"] == "data/tomo/tomo_001_segmentation.mrcseg"
    ]
    assert seg_row.iloc[0][source_col] == "Specimen_001 denoised_tomogram"


def test_source_image_types_only_accepts_segmentation_target():
    with pytest.raises(ValueError, match="Valid targets: \\['segmentation'\\]"):
        SpecimenTrackAssignmentConfig(
            source_image_types={"tomogram": "aligned_tilt_series"}
        )


def test_track_metadata_requires_dataset_for_path():
    schema = {
        "_:col0": ro_crate_models.Column(
            **{
                "@id": "_:col0",
                "@type": ["csvw:Column"],
                "columnName": "file_path",
                "propertyUrl": str(BIA.filePath),
            }
        )
    }
    file_list = FileList(
        schema=schema,
        data=pd.DataFrame({"file_path": ["data/tomo/tomo_001.mrc"]}),
    )
    track = SpecimenTrack(
        specimen_id="001",
        tomogram=Path("data/tomo/tomo_001.mrc"),
    )
    dataset_config = DatasetModificationConfig(
        name="Reconstructed tomograms",
        specimen_tracks=SpecimenTrackAssignmentConfig(
            protocol_titles={"tomogram": "Tomogram reconstruction"}
        ),
    )

    with pytest.raises(ValueError, match="no dataset recorded"):
        _write_associated_protocol(
            file_list=file_list,
            tracks=[track],
            dataset_configs=[dataset_config],
        )


def _setup_and_run(tmp_path: Path, accession_id: str) -> tuple[dict, pd.DataFrame]:
    """
    Copy the minimal RO-Crate into tmp_path, run the modify-roc CLI against
    the fixture modification config, and return (graph_by_id, file_list_df).
    """
    src = _fixture_root() / accession_id
    dest_crate = tmp_path / accession_id
    shutil.copytree(src / "minimal", dest_crate)
    config_path = src / "modification_config.yaml"

    result = runner.invoke(
        ro_crate_ingest,
        ["modify-roc", str(dest_crate), str(config_path)],
    )

    if result.exit_code != 0:
        tb = (
            "".join(traceback.format_exception(result.exception))
            if result.exception
            else result.output
        )
        pytest.fail(
            f"modify-roc CLI failed for {accession_id} "
            f"(exit code {result.exit_code}):\n{tb}"
        )

    output_dir = dest_crate / "modified"
    with open(output_dir / "ro-crate-metadata.json") as f:
        crate = json.load(f)
    graph_by_id = {e["@id"]: e for e in crate["@graph"]}

    tsv_files = list(output_dir.glob("*.tsv"))
    assert (
        len(tsv_files) == 1
    ), f"Expected exactly one TSV in output, found: {tsv_files}"
    df = pd.read_csv(tsv_files[0], sep="\t", dtype=str)

    return graph_by_id, df


@pytest.fixture(scope="class")
def imagegroups_outputs(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("imagegroups")
    return _setup_and_run(tmp, "MODIFY-ROC-IMAGEGROUPS")


@pytest.fixture(scope="class")
def specimens_outputs(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("specimens")
    return _setup_and_run(tmp, "MODIFY-ROC-SPECIMENS")


@pytest.fixture(scope="class")
def annotations_outputs(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("annotations")
    return _setup_and_run(tmp, "MODIFY-ROC-ANNOTATIONS")


class TestImageGroups:
    """
    MODIFY-ROC-IMAGEGROUPS:
    Full comparison against expected output, plus targeted checks on the
    image_groups feature specifically under test:
    - *.tif files get associated_protocol: #Fluorescence%20imaging%20protocol
    - *.png files get associated_protocol: #Phase%20contrast%20imaging%20protocol
    - data/README.txt lands in the automatic Default dataset.
    """

    ACCESSION_ID = "MODIFY-ROC-IMAGEGROUPS"

    @pytest.fixture(autouse=True)
    def load_outputs(self, imagegroups_outputs):
        self.graph, self.df = imagegroups_outputs

    # --- Full output comparison ---------------------------------------------
    def test_metadata_graph_matches_expected(self):
        expected_path = (
            _fixture_root() / self.ACCESSION_ID / "modified" / "ro-crate-metadata.json"
        )
        with open(expected_path) as f:
            expected = json.load(f)
        expected_graph = {e["@id"]: e for e in expected["@graph"]}
        assert sorted(self.graph.keys()) == sorted(expected_graph.keys()), (
            f"Graph @id sets differ.\n"
            f"  Extra in output:   {sorted(set(self.graph) - set(expected_graph))}\n"
            f"  Missing in output: {sorted(set(expected_graph) - set(self.graph))}"
        )
        for eid, entity in expected_graph.items():
            assert self.graph[eid] == entity, (
                f"Entity {eid!r} differs from expected.\n"
                f"  Expected: {entity}\n"
                f"  Got:      {self.graph[eid]}"
            )

    def test_file_list_matches_expected(self):
        expected_path = (
            _fixture_root() / self.ACCESSION_ID / "modified" / "file_list.tsv"
        )
        expected_df = pd.read_csv(expected_path, sep="\t", dtype=str)
        df_sorted = self.df.sort_values("file_path").reset_index(drop=True)
        expected_sorted = expected_df.sort_values("file_path").reset_index(drop=True)
        pd.testing.assert_frame_equal(df_sorted, expected_sorted)

    # --- Targeted: image_groups protocol assignment -------------------------
    def test_tif_files_get_fluorescence_protocol(self):
        tif_rows = self.df[self.df["file_path"].str.endswith(".tif")]
        expected = title_to_id("Fluorescence imaging protocol")
        assert (tif_rows["associated_protocol"] == expected).all(), (
            f"Expected .tif files to have protocol {expected!r}, "
            f"got:\n{tif_rows[['file_path', 'associated_protocol']]}"
        )

    def test_png_files_get_phase_contrast_protocol(self):
        png_rows = self.df[self.df["file_path"].str.endswith(".png")]
        expected = title_to_id("Phase contrast imaging protocol")
        assert (png_rows["associated_protocol"] == expected).all(), (
            f"Expected .png files to have protocol {expected!r}, "
            f"got:\n{png_rows[['file_path', 'associated_protocol']]}"
        )

    def test_different_image_types_get_different_protocols(self):
        """Core image_groups invariant: file type determines protocol."""
        tif_protocol = self.df[self.df["file_path"].str.endswith(".tif")].iloc[0][
            "associated_protocol"
        ]
        png_protocol = self.df[self.df["file_path"].str.endswith(".png")].iloc[0][
            "associated_protocol"
        ]
        assert (
            tif_protocol != png_protocol
        ), "Expected .tif and .png files to receive different protocols"

    # --- Targeted: default dataset ------------------------------------------
    def test_unassigned_file_goes_to_default_dataset(self):
        row = self.df[self.df["file_path"] == "data/README.txt"]
        assert len(row) == 1
        assert row.iloc[0]["dataset"] == title_to_id(
            "Default dataset"
        ), f"Expected README.txt in Default dataset, got {row.iloc[0]['dataset']!r}"

    def test_default_dataset_is_part_of_study(self):
        study = self.graph["./"]
        assert {"@id": title_to_id("Default dataset")} in study["hasPart"]

    def test_no_specimen_entities_created(self):
        specimen_ids = [k for k in self.graph if "Specimen_" in k]
        assert (
            specimen_ids == []
        ), f"Expected no Specimen entities, found: {specimen_ids}"


class TestSpecimenTracksWithAdditionalFiles:
    """
    MODIFY-ROC-SPECIMENS:
    Full comparison against expected output, plus targeted checks on the
    specimen track features specifically under test:
    - Three specimen entities created (001, 002, 003), where 003 comes from
      the additional_files assignment of data/extra/ts_003.mrc.st.
    - Specimen group override: specimen 002 uses 'HeLa cells (mutant)'.
    - One annotation row points to the specimen-generated tomogram label.
    - Segmentation image rows are typed as images, labelled, linked to their
      upstream tomograms, and associated with an AnnotationMethod.
    - associated_source_image, associated_subject, associated_protocol written
      correctly in the file list.
    """

    ACCESSION_ID = "MODIFY-ROC-SPECIMENS"

    @pytest.fixture(autouse=True)
    def load_outputs(self, specimens_outputs):
        self.graph, self.df = specimens_outputs

    # --- Full output comparison ---------------------------------------------
    def test_metadata_graph_matches_expected(self):
        expected_path = (
            _fixture_root() / self.ACCESSION_ID / "modified" / "ro-crate-metadata.json"
        )
        with open(expected_path) as f:
            expected = json.load(f)
        expected_graph = {e["@id"]: e for e in expected["@graph"]}
        assert sorted(self.graph.keys()) == sorted(expected_graph.keys()), (
            f"Graph @id sets differ.\n"
            f"  Extra in output:   {sorted(set(self.graph) - set(expected_graph))}\n"
            f"  Missing in output: {sorted(set(expected_graph) - set(self.graph))}"
        )
        for eid, entity in expected_graph.items():
            assert self.graph[eid] == entity, (
                f"Entity {eid!r} differs from expected.\n"
                f"  Expected: {entity}\n"
                f"  Got:      {self.graph[eid]}"
            )

    def test_file_list_matches_expected(self):
        expected_path = (
            _fixture_root() / self.ACCESSION_ID / "modified" / "file_list.tsv"
        )
        expected_df = pd.read_csv(expected_path, sep="\t", dtype=str)
        # Sort both by file_path for stable comparison
        df_sorted = self.df.sort_values("file_path").reset_index(drop=True)
        expected_sorted = expected_df.sort_values("file_path").reset_index(drop=True)
        pd.testing.assert_frame_equal(df_sorted, expected_sorted)

    # --- Targeted: specimen entities and metadata ---------------------------
    def test_three_specimen_entities_created(self):
        for sid in ("001", "002", "003"):
            eid = title_to_id(f"Specimen_{sid}")
            assert eid in self.graph, f"Expected {eid!r} in graph"

    def test_specimen_001_wild_type_biosample(self):
        entity = self.graph[title_to_id("Specimen_001")]
        expected = {"@id": title_to_id("HeLa cells (wild type)")}
        assert expected in entity.get("biologicalEntity", []), (
            f"Specimen_001: expected biologicalEntity to contain {expected!r}, "
            f"got {entity.get('biologicalEntity')}"
        )

    def test_specimen_002_override_uses_mutant_biosample(self):
        entity = self.graph[title_to_id("Specimen_002")]
        expected = {"@id": title_to_id("HeLa cells (mutant)")}
        assert expected in entity.get("biologicalEntity", []), (
            f"Specimen_002: expected biosample override to {expected!r}, "
            f"got {entity.get('biologicalEntity')}"
        )

    def test_specimen_003_from_additional_files(self):
        """Specimen 003 exists only because additional_files assigned ts_003."""
        assert title_to_id("Specimen_003") in self.graph
        row = self.df[self.df["file_path"] == "data/extra/ts_003.mrc.st"]
        assert row.iloc[0]["associated_subject"] == title_to_id("Specimen_003")

    # --- Targeted: file list specimen track columns -------------------------
    def test_tilt_series_have_associated_subject(self):
        for path, sid in [
            ("data/ts/ts_001.mrc.st", "001"),
            ("data/ts/ts_002.mrc.st", "002"),
            ("data/extra/ts_003.mrc.st", "003"),
        ]:
            row = self.df[self.df["file_path"] == path]
            assert row.iloc[0]["associated_subject"] == title_to_id(
                f"Specimen_{sid}"
            ), f"{path}: unexpected associated_subject {row.iloc[0]['associated_subject']!r}"

    def test_tomograms_have_associated_source_image(self):
        for path, sid in [
            ("data/tomo/tomo_001.mrc", "001"),
            ("data/tomo/tomo_002.mrc", "002"),
        ]:
            row = self.df[self.df["file_path"] == path]
            assert (
                row.iloc[0]["associated_source_image"] == f"Specimen_{sid} tilt_series"
            ), f"{path}: unexpected associated_source_image {row.iloc[0]['associated_source_image']!r}"

    def test_annotation_points_to_generated_tomogram_label(self):
        annotation_row = self.df[
            self.df["file_path"] == "data/annotations/tomo_001_segmentation.csv"
        ]
        tomogram_row = self.df[self.df["file_path"] == "data/tomo/tomo_001.mrc"]

        assert len(annotation_row) == 1
        assert len(tomogram_row) == 1
        assert annotation_row.iloc[0]["type"] == "http://bia/AnnotationData"
        assert annotation_row.iloc[0]["associated_annotation_method"] == title_to_id(
            "Tomogram segmentation"
        )
        assert (
            annotation_row.iloc[0]["associated_source_image"]
            == tomogram_row.iloc[0]["label"]
        )
        assert (
            annotation_row.iloc[0]["associated_source_image"] == "Specimen_001 tomogram"
        )

    def test_non_track_labels_are_preserved(self):
        row = self.df[self.df["file_path"] == "data/README.md"]
        assert row.iloc[0]["label"] == "Readme label"

    def test_tomograms_have_reconstruction_protocol(self):
        tomo_rows = self.df[self.df["file_path"].str.endswith(".mrc")]
        expected = title_to_id("Tomogram reconstruction")
        assert (tomo_rows["associated_protocol"] == expected).all(), (
            f"Expected all tomograms to have protocol {expected!r}, "
            f"got:\n{tomo_rows[['file_path', 'associated_protocol']]}"
        )

    def test_segmentations_are_images(self):
        seg_rows = self.df[self.df["file_path"].str.endswith(".mrcseg")]
        assert len(seg_rows) == 3
        assert (seg_rows["type"] == "http://bia/Image").all()

    def test_segmentations_link_to_upstream_tomogram(self):
        expected = {
            "data/tomo/tomo_001_segmentation_a.mrcseg": "Specimen_001 tomogram",
            "data/tomo/tomo_001_segmentation_b.mrcseg": "Specimen_001 tomogram",
            "data/tomo/tomo_002_segmentation.mrcseg": "Specimen_002 tomogram",
        }
        for path, source_image in expected.items():
            row = self.df[self.df["file_path"] == path]
            assert row.iloc[0]["associated_source_image"] == source_image, (
                f"{path}: unexpected associated_source_image "
                f"{row.iloc[0]['associated_source_image']!r}"
            )

    def test_multiple_segmentations_get_unique_labels(self):
        labels = set(
            self.df[self.df["file_path"].str.endswith(".mrcseg")]["label"].dropna()
        )
        assert "Specimen_001 segmentation_tomo_001_segmentation_a" in labels
        assert "Specimen_001 segmentation_tomo_001_segmentation_b" in labels
        assert "Specimen_002 segmentation" in labels

    def test_segmentation_annotation_method_entity_created(self):
        annotation_method = self.graph[title_to_id("Manual tomogram segmentation")]
        assert annotation_method["methodType"] == ["segmentation_mask"]

    def test_segmentations_have_annotation_method(self):
        seg_rows = self.df[self.df["file_path"].str.endswith(".mrcseg")]
        expected = title_to_id("Manual tomogram segmentation")
        assert (seg_rows["associated_annotation_method"] == expected).all(), (
            f"Expected segmentations to have annotation method {expected!r}, "
            f"got:\n{seg_rows[['file_path', 'associated_annotation_method']]}"
        )

    def test_segmentation_dataset_has_annotation_method_association(self):
        dataset = self.graph[title_to_id("Reconstructed tomograms")]
        expected = {"@id": title_to_id("Manual tomogram segmentation")}
        assert expected in dataset.get("associatedAnnotationMethod", []), (
            "Expected Reconstructed tomograms dataset to reference segmentation "
            f"annotation method, got {dataset.get('associatedAnnotationMethod')}"
        )


class TestAnnotations:
    """
    MODIFY-ROC-ANNOTATIONS:
    Full comparison against expected output, plus targeted checks on annotation
    assignment and image-group protocol assignment in a mixed image/annotation
    dataset.
    """

    ACCESSION_ID = "MODIFY-ROC-ANNOTATIONS"

    @pytest.fixture(autouse=True)
    def load_outputs(self, annotations_outputs):
        self.graph, self.df = annotations_outputs

    # --- Full output comparison ---------------------------------------------
    def test_metadata_graph_matches_expected(self):
        expected_path = (
            _fixture_root() / self.ACCESSION_ID / "modified" / "ro-crate-metadata.json"
        )
        with open(expected_path) as f:
            expected = json.load(f)
        expected_graph = {e["@id"]: e for e in expected["@graph"]}
        assert sorted(self.graph.keys()) == sorted(expected_graph.keys()), (
            f"Graph @id sets differ.\n"
            f"  Extra in output:   {sorted(set(self.graph) - set(expected_graph))}\n"
            f"  Missing in output: {sorted(set(expected_graph) - set(self.graph))}"
        )
        for eid, entity in expected_graph.items():
            assert self.graph[eid] == entity, (
                f"Entity {eid!r} differs from expected.\n"
                f"  Expected: {entity}\n"
                f"  Got:      {self.graph[eid]}"
            )

    def test_file_list_matches_expected(self):
        expected_path = (
            _fixture_root() / self.ACCESSION_ID / "modified" / "file_list.tsv"
        )
        expected_df = pd.read_csv(expected_path, sep="\t", dtype=str)
        df_sorted = self.df.sort_values("file_path").reset_index(drop=True)
        expected_sorted = expected_df.sort_values("file_path").reset_index(drop=True)
        pd.testing.assert_frame_equal(df_sorted, expected_sorted)

    # --- Targeted: annotation assignment -------------------------------------
    def test_annotation_method_entity_created(self):
        assert title_to_id("Cell segmentation") in self.graph

    def test_annotation_row_gets_annotation_data_type(self):
        row = self.df[self.df["file_path"] == "data/annotations/cell_001_mask.csv"]
        assert len(row) == 1
        assert row.iloc[0]["type"] == "http://bia/AnnotationData"

    def test_annotation_row_gets_expected_metadata(self):
        row = self.df[self.df["file_path"] == "data/annotations/cell_001_mask.csv"]
        assert row.iloc[0]["label"] == "cell_001_mask"
        assert row.iloc[0]["associated_annotation_method"] == title_to_id(
            "Cell segmentation"
        )
        assert row.iloc[0]["associated_source_image"] == "Cell 001 fluorescence image"

    def test_annotation_row_gets_associated_source_image_column(self):
        assert "associated_source_image" in self.df.columns
        assert "source_image_label" not in self.df.columns
        row = self.df[self.df["file_path"] == "data/annotations/cell_001_mask.csv"]
        assert row.iloc[0]["associated_source_image"] == "Cell 001 fluorescence image"

    # --- Targeted: image_groups protocol assignment -------------------------
    def test_annotation_fixture_tif_images_get_protocol(self):
        tif_rows = self.df[self.df["file_path"].str.endswith(".tif")]
        expected = title_to_id("Fluorescence imaging protocol")
        assert (tif_rows["associated_protocol"] == expected).all(), (
            f"Expected annotation fixture .tif images to have protocol {expected!r}, "
            f"got:\n{tif_rows[['file_path', 'associated_protocol']]}"
        )

    def test_annotation_fixture_png_images_get_protocol(self):
        png_rows = self.df[self.df["file_path"].str.endswith(".png")]
        expected = title_to_id("Phase contrast imaging protocol")
        assert (png_rows["associated_protocol"] == expected).all(), (
            f"Expected annotation fixture .png images to have protocol {expected!r}, "
            f"got:\n{png_rows[['file_path', 'associated_protocol']]}"
        )
