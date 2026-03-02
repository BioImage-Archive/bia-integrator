import pytest
import yaml
from pathlib import Path
from typer.testing import CliRunner

from ro_crate_ingest.cli import ro_crate_ingest

runner = CliRunner()

TEST_DIR = Path(__file__).parent


def get_proposal_config_path(accession_id: str) -> Path:
    filename = accession_id.lower().replace("-", "_")
    return TEST_DIR / "empiar_proposal_generation" / "proposal_configs" / f"{filename}.yaml"


def get_expected_proposal_path(accession_id: str) -> Path:
    filename = accession_id.lower().replace("-", "_")
    return TEST_DIR / "empiar_proposal_generation" / "output_data" / f"{filename}.yaml"


def get_proposal_input_path(accession_id: str, tmp_proposal_dir: Path) -> Path:
    """
    Return the path to the proposal that stage 2 should consume.
    Uses the checked-in expected proposal so stage 2 can run independently.
    """
    return get_expected_proposal_path(accession_id)


@pytest.fixture
def tmp_proposal_dir(tmp_path: Path) -> Path:
    d = tmp_path / "proposals"
    d.mkdir()
    return d


@pytest.fixture
def tmp_ro_crate_dir(tmp_path: Path) -> Path:
    d = tmp_path / "ro_crates"
    d.mkdir()
    return d


def _load_yaml(path: Path) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def _specimens_by_title(proposal: dict) -> dict[str, dict]:
    return {
        s["title"]: s
        for s in proposal.get("rembis", {}).get("Specimen", [])
    }


def _dataset_by_title(proposal: dict, title: str) -> dict | None:
    for ds in proposal.get("datasets", []):
        if ds.get("title") == title:
            return ds
    return None


def _assigned_image_by_label(dataset: dict, label: str) -> dict | None:
    for ai in dataset.get("assigned_images", []):
        # Images may use "label" (single) or "label_prefix" (frames)
        if ai.get("label") == label or ai.get("label_prefix") == label:
            return ai
    return None


@pytest.mark.parametrize(
    "accession_id",
    [
        "EMPIAR-SPECIMENPATTERNTEST",
        "EMPIAR-SPECIMENALIASPATTERNSTEST",
        "EMPIAR-SPECIMENALIASMAPPINGSTEST",
        "EMPIAR-SPECIMENGROUPTEST",
        "EMPIAR-ENTRYWITHOUTFRAMESTEST",
    ],
)
def test_proposal_matches_expected(accession_id: str, tmp_proposal_dir: Path):
    """The generated proposal matches the checked-in expected proposal exactly."""
    config_path = get_proposal_config_path(accession_id)
    result = runner.invoke(
        ro_crate_ingest,
        ["generate-empiar-proposal", str(config_path), "-p", str(tmp_proposal_dir)],
    )
    assert result.exit_code == 0, f"CLI failed:\n{result.output}"

    filename = accession_id.lower().replace("-", "_") + ".yaml"
    created_proposal = _load_yaml(tmp_proposal_dir / filename)
    expected_proposal = _load_yaml(get_expected_proposal_path(accession_id))

    assert created_proposal == expected_proposal


class TestSpecimenPattern:
    """
    Case 1: simple regex patterns — tomo_(\d{4})
    Accession-ID: EMPIAR-SPECIMENPATTERNTEST
    """

    accession_id = "EMPIAR-SPECIMENPATTERNTEST"

    @pytest.fixture(autouse=True)
    def _proposal(self, tmp_proposal_dir):
        config_path = get_proposal_config_path(self.accession_id)
        runner.invoke(
            ro_crate_ingest,
            ["generate-empiar-proposal", str(config_path), "-p", str(tmp_proposal_dir)],
        )
        filename = self.accession_id.lower().replace("-", "_") + ".yaml"
        self.proposal = _load_yaml(tmp_proposal_dir / filename)

    def test_three_specimens_created(self):
        specimens = _specimens_by_title(self.proposal)
        assert len(specimens) == 3

    def test_specimen_ids_extracted_correctly(self):
        specimens = _specimens_by_title(self.proposal)
        assert "Specimen_0001" in specimens
        assert "Specimen_0002" in specimens
        assert "Specimen_0003" in specimens

    def test_all_specimens_inherit_global_defaults(self):
        specimens = _specimens_by_title(self.proposal)
        for spec in specimens.values():
            assert spec["biosample_title"] == "Test organism cells"
            assert "Grid preparation" in spec["specimen_imaging_preparation_protocol_title"]

    def test_frames_dataset_has_iap(self):
        ds = _dataset_by_title(self.proposal, "Raw frames")
        assert ds is not None
        rembis = ds.get("assigned_dataset_rembis", [])
        assert any(
            r.get("image_acquisition_protocol_title") == "Cryo-electron tomography"
            for r in rembis
        )

    def test_tilt_series_linked_to_frames(self):
        ds = _dataset_by_title(self.proposal, "Tilt series")
        assert ds is not None
        ai = _assigned_image_by_label(ds, "Specimen_0001 tilt_series")
        assert ai is not None
        assert "input_label_prefix" in ai or "input_file_pattern" in ai

    def test_tomogram_linked_to_tilt_series(self):
        ds = _dataset_by_title(self.proposal, "Tomograms")
        assert ds is not None
        ai = _assigned_image_by_label(ds, "Specimen_0001 tomogram")
        assert ai is not None
        assert ai.get("input_label") == "Specimen_0001 tilt_series"

    def test_protocol_titles_assigned_to_tilt_series(self):
        ds = _dataset_by_title(self.proposal, "Tilt series")
        ai = _assigned_image_by_label(ds, "Specimen_0001 tilt_series")
        assert ai is not None
        assert ai.get("protocol_title") == "Tilt series pre-processing"

    def test_protocol_titles_assigned_to_tomograms(self):
        ds = _dataset_by_title(self.proposal, "Tomograms")
        ai = _assigned_image_by_label(ds, "Specimen_0001 tomogram")
        assert ai is not None
        assert ai.get("protocol_title") == "Tomogram reconstruction"


class TestSpecimenAliasPatterns:
    """
    Case 2: pattern_alias_mappings — different formats, same underlying id.
    Accession-ID: EMPIAR-SPECIMENALIASPATTERNSTEST
    """

    accession_id = "EMPIAR-SPECIMENALIASPATTERNSTEST"

    @pytest.fixture(autouse=True)
    def _proposal(self, tmp_proposal_dir):
        config_path = get_proposal_config_path(self.accession_id)
        runner.invoke(
            ro_crate_ingest,
            ["generate-empiar-proposal", str(config_path), "-p", str(tmp_proposal_dir)],
        )
        filename = self.accession_id.lower().replace("-", "_") + ".yaml"
        self.proposal = _load_yaml(tmp_proposal_dir / filename)

    def test_three_specimens_created(self):
        specimens = _specimens_by_title(self.proposal)
        assert len(specimens) == 3

    def test_canonical_ids_used(self):
        """Specimens should be keyed by the canonical 4-digit form."""
        specimens = _specimens_by_title(self.proposal)
        assert "Specimen_0001" in specimens
        assert "Specimen_0002" in specimens
        assert "Specimen_0003" in specimens

    def test_frames_tilt_series_tomograms_linked_per_specimen(self):
        """
        Despite three different naming conventions across the three datasets,
        each specimen's track should chain frames → tilt series → tomogram.
        """
        for n in ["0001", "0002", "0003"]:
            ts_ds = _dataset_by_title(self.proposal, "Tilt series")
            ts_ai = _assigned_image_by_label(ts_ds, f"Specimen_{n} tilt_series")
            assert ts_ai is not None, f"No tilt series entry for Specimen_{n}"
            assert "input_label_prefix" in ts_ai or "input_file_pattern" in ts_ai

            tomo_ds = _dataset_by_title(self.proposal, "Tomograms")
            tomo_ai = _assigned_image_by_label(tomo_ds, f"Specimen_{n} tomogram")
            assert tomo_ai is not None, f"No tomogram entry for Specimen_{n}"
            assert tomo_ai.get("input_label") == f"Specimen_{n} tilt_series"


class TestSpecimenAliasMappings:
    """
    Case 3: literal_alias_mappings — arbitrary glob-to-id lookup.
    Accession-ID: EMPIAR-SPECIMENALIASMAPPINGSTEST
    """

    accession_id = "EMPIAR-SPECIMENALIASMAPPINGSTEST"

    @pytest.fixture(autouse=True)
    def _proposal(self, tmp_proposal_dir):
        config_path = get_proposal_config_path(self.accession_id)
        runner.invoke(
            ro_crate_ingest,
            ["generate-empiar-proposal", str(config_path), "-p", str(tmp_proposal_dir)],
        )
        filename = self.accession_id.lower().replace("-", "_") + ".yaml"
        self.proposal = _load_yaml(tmp_proposal_dir / filename)

    def test_three_specimens_created(self):
        specimens = _specimens_by_title(self.proposal)
        assert len(specimens) == 3

    def test_canonical_ids_used(self):
        specimens = _specimens_by_title(self.proposal)
        assert "Specimen_specimen_01" in specimens
        assert "Specimen_specimen_02" in specimens
        assert "Specimen_specimen_03" in specimens

    def test_frames_linked_via_date_path(self):
        """
        Frames are under dated session dirs; the literal mapping should still
        pick them up and link them into the track.
        """
        ds = _dataset_by_title(self.proposal, "Tilt series")
        ai = _assigned_image_by_label(ds, "Specimen_specimen_01 tilt_series")
        assert ai is not None
        # Frames were found, so there should be an input link back to them.
        assert "input_label_prefix" in ai or "input_file_pattern" in ai

    def test_tomograms_linked_by_name(self):
        ds = _dataset_by_title(self.proposal, "Tomograms")
        ai = _assigned_image_by_label(ds, "Specimen_specimen_01 tomogram")
        assert ai is not None
        assert ai.get("input_label") == "Specimen_specimen_01 tilt_series"


class TestSpecimenGroupOverride:
    """
    specimen_groups on the tilt series dataset overrides biosample and prep
    protocol for specimen_03 only; specimens 01 and 02 use global defaults.
    Accession-ID: EMPIAR-SPECIMENGROUPTEST
    """

    accession_id = "EMPIAR-SPECIMENGROUPTEST"

    @pytest.fixture(autouse=True)
    def _proposal(self, tmp_proposal_dir):
        config_path = get_proposal_config_path(self.accession_id)
        runner.invoke(
            ro_crate_ingest,
            ["generate-empiar-proposal", str(config_path), "-p", str(tmp_proposal_dir)],
        )
        filename = self.accession_id.lower().replace("-", "_") + ".yaml"
        self.proposal = _load_yaml(tmp_proposal_dir / filename)

    def test_three_specimens_created(self):
        specimens = _specimens_by_title(self.proposal)
        assert len(specimens) == 3

    def test_default_specimens_have_condition_a_biosample(self):
        specimens = _specimens_by_title(self.proposal)
        for sid in ["Specimen_0001", "Specimen_0002"]:
            assert specimens[sid]["biosample_title"] == "Test organism cells, condition A"

    def test_overridden_specimen_has_condition_b_biosample(self):
        specimens = _specimens_by_title(self.proposal)
        assert specimens["Specimen_0003"]["biosample_title"] == "Test organism cells, condition B"

    def test_overridden_specimen_has_alternative_prep_protocol(self):
        specimens = _specimens_by_title(self.proposal)
        preps = specimens["Specimen_0003"]["specimen_imaging_preparation_protocol_title"]
        assert "Alternative grid preparation" in preps
        assert "Grid preparation" not in preps

    def test_default_specimens_have_standard_prep_protocols(self):
        specimens = _specimens_by_title(self.proposal)
        for sid in ["Specimen_0001", "Specimen_0002"]:
            preps = specimens[sid]["specimen_imaging_preparation_protocol_title"]
            assert "Grid preparation" in preps


class TestEntryWithoutFrames:
    """
    No frames dataset is configured. Tilt series are track_start; specimens
    should be assigned at the tilt series level.
    Accession-ID: EMPIAR-ENTRYWITHOUTFRAMESTEST
    """

    accession_id = "EMPIAR-ENTRYWITHOUTFRAMESTEST"

    @pytest.fixture(autouse=True)
    def _proposal(self, tmp_proposal_dir):
        config_path = get_proposal_config_path(self.accession_id)
        runner.invoke(
            ro_crate_ingest,
            ["generate-empiar-proposal", str(config_path), "-p", str(tmp_proposal_dir)],
        )
        filename = self.accession_id.lower().replace("-", "_") + ".yaml"
        self.proposal = _load_yaml(tmp_proposal_dir / filename)

    def test_three_specimens_created(self):
        specimens = _specimens_by_title(self.proposal)
        assert len(specimens) == 3

    def test_no_frames_dataset_in_output(self):
        titles = [ds.get("title") for ds in self.proposal.get("datasets", [])]
        assert "Raw frames" not in titles

    def test_tilt_series_has_specimen_title_not_input_link(self):
        """
        With no frames, tilt series entries should carry specimen_title
        (they are the track start) rather than an input_label_prefix.
        """
        ds = _dataset_by_title(self.proposal, "Tilt series")
        for n in ["0001", "0002", "0003"]:
            ai = _assigned_image_by_label(ds, f"Specimen_{n} tilt_series")
            assert ai is not None
            assert "specimen_title" in ai
            assert "input_label_prefix" not in ai
            assert "input_file_pattern" not in ai

    def test_tomograms_linked_to_tilt_series(self):
        ds = _dataset_by_title(self.proposal, "Tomograms")
        for n in ["0001", "0002", "0003"]:
            ai = _assigned_image_by_label(ds, f"Specimen_{n} tomogram")
            assert ai is not None
            assert ai.get("input_label") == f"Specimen_{n} tilt_series"

    def test_iap_on_tilt_series_dataset(self):
        """
        With no frames, the IAP should move to the tilt series dataset block.
        """
        ds = _dataset_by_title(self.proposal, "Tilt series")
        rembis = ds.get("assigned_dataset_rembis", [])
        assert any(
            r.get("image_acquisition_protocol_title") == "Cryo-electron tomography"
            for r in rembis
        )
