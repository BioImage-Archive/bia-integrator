import re
from pydantic import BaseModel, Field, ConfigDict, BeforeValidator, model_validator
from typing import Annotated, Self

from ro_crate_ingest.ro_crate_modification.enrichment.image_types import ImageType


# Valid keys for ImageAssignmentConfig.by_type: all ImageType values plus the
# non-track-aware "image" sentinel for files that are images but don't belong
# to a specimen track.
IMAGE_ASSIGNMENT_TYPE_KEY = "image"
_VALID_BY_TYPE_KEYS: frozenset[str] = frozenset(t.value for t in ImageType) | {IMAGE_ASSIGNMENT_TYPE_KEY}


def _string_to_list(value):
    if isinstance(value, str):
        return [value]
    return value


def _validate_regex(pattern: str, location: str) -> None:
    try:
        re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"{location}: invalid regex '{pattern}': {exc}") from exc


def _validate_regex_has_capture_group(pattern: str, location: str) -> None:
    _validate_regex(pattern, location)
    if not re.search(r'\((?!\?(?::|!|=|<!|<=))', pattern):
        raise ValueError(
            f"{location}: regex '{pattern}' has no capturing group. "
            "Specimen ID extraction requires at least one."
        )


class ClosedBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Study component model — for adding information to study entity
# ---------------------------------------------------------------------------
class StudyMetadata(ClosedBaseModel):
    description: str | None = None
    see_also: list[str] = Field(default_factory=list)
    related_publication: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# REMBI component models — study-wide, not dataset-specific
# ---------------------------------------------------------------------------

class Taxon(ClosedBaseModel):
    common_name: str
    scientific_name: str
    ncbi_id: str | None = Field(None)


class Biosample(ClosedBaseModel):
    title: str
    biological_entity_description: str
    organism_classification: list[Taxon]
    growth_protocol_title: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )


class ImageAcquisitionProtocol(ClosedBaseModel):
    title: str
    protocol_description: str
    imaging_instrument_description: str
    fbbi_id: list[str]
    imaging_method_name: list[str]


class SpecimenImagingPreparationProtocol(ClosedBaseModel):
    title: str
    protocol_description: str


class Protocol(ClosedBaseModel):
    title: str
    protocol_description: str


class AnnotationMethod(ClosedBaseModel):
    title: str
    protocol_description: str
    method_type: list[str]


class RembiByType(ClosedBaseModel):
    """
    Study-wide REMBI components to add to the RO-Crate metadata. Not inherently 
    tied to any specific dataset. Specimens are handled separately via SpecimenDefaults
    and SpecimenGroup, as they are generated from tracks and reference these
    components by title.
    """
    biosamples: list[Biosample] = Field(default_factory=list)
    image_acquisition_protocols: list[ImageAcquisitionProtocol] = Field(default_factory=list)
    specimen_imaging_preparation_protocols: list[SpecimenImagingPreparationProtocol] = Field(
        default_factory=list
    )
    protocols: list[Protocol] = Field(default_factory=list)
    annotation_methods: list[AnnotationMethod] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Specimen metadata models — top-level, cross-dataset
# ---------------------------------------------------------------------------

class SpecimenDefaults(ClosedBaseModel):
    """
    Default metadata applied to every specimen discovered via track
    identification. Overridden per-specimen or per-group via SpecimenGroup
    entries in DatasetModificationConfig blocks.
    """
    biosample_title: str | None = None
    specimen_imaging_preparation_protocol_titles: Annotated[
        list[str], BeforeValidator(_string_to_list)
    ] = Field(default_factory=list)


class SpecimenTrackConfig(ClosedBaseModel):
    """
    Cross-dataset specimen ID extraction strategy.
    Exactly one identification strategy may be active.

    patterns
        Simple regex list. Each pattern must contain at least one capture group.

    pattern_alias_mappings
        Dict mapping a canonical regex pattern (with a \\d{N} group) to a list
        of alias patterns. For IDs that appear in different zero-padded forms
        across datasets.

    literal_alias_mappings
        Dict mapping a canonical specimen ID to a list of glob aliases. For
        cases where there is no algorithmic link between a specimen's files.
    """
    patterns: list[str] = Field(default_factory=list)
    pattern_alias_mappings: dict[str, list[str]] = Field(default_factory=dict)
    literal_alias_mappings: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_strategies(self) -> Self:
        active = sum([
            bool(self.patterns),
            bool(self.pattern_alias_mappings),
            bool(self.literal_alias_mappings),
        ])
        if active > 1:
            raise ValueError(
                "specimen_tracks: only one of 'patterns', 'pattern_alias_mappings', "
                "or 'literal_alias_mappings' may be non-empty."
            )

        for i, pattern in enumerate(self.patterns):
            _validate_regex_has_capture_group(pattern, f"specimen_tracks.patterns[{i}]")

        for canonical, aliases in self.pattern_alias_mappings.items():
            _validate_regex_has_capture_group(
                canonical, f"specimen_tracks.pattern_alias_mappings key '{canonical}'"
            )
            if not re.search(r'\\d\{\d+\}', canonical):
                raise ValueError(
                    f"specimen_tracks.pattern_alias_mappings: canonical pattern '{canonical}' "
                    r"must contain a \d{N} group for zero-padding transformation."
                )
            for j, alias in enumerate(aliases):
                _validate_regex_has_capture_group(
                    alias,
                    f"specimen_tracks.pattern_alias_mappings['{canonical}'][{j}]",
                )

        return self


class SpecimenGroup(ClosedBaseModel):
    """
    Per-specimen or per-pattern metadata override, scoped to a dataset block.
    Exactly one of specimen_ids or specimen_id_pattern must be set.
    At least one metadata override field must be present.
    """
    specimen_ids: list[str] = Field(default_factory=list)
    specimen_id_pattern: str | None = None
    biosample_title: str | None = None
    specimen_imaging_preparation_protocol_titles: Annotated[
        list[str], BeforeValidator(_string_to_list)
    ] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_group(self) -> Self:
        has_ids = bool(self.specimen_ids)
        has_pattern = self.specimen_id_pattern is not None

        if has_ids and has_pattern:
            raise ValueError(
                "specimen_groups entry: 'specimen_ids' and 'specimen_id_pattern' "
                "are mutually exclusive."
            )
        if not has_ids and not has_pattern:
            raise ValueError(
                "specimen_groups entry: one of 'specimen_ids' or "
                "'specimen_id_pattern' must be provided."
            )

        has_override = (
            self.biosample_title is not None
            or bool(self.specimen_imaging_preparation_protocol_titles)
        )
        if not has_override:
            raise ValueError(
                "specimen_groups entry: at least one metadata override field "
                "('biosample_title' or 'specimen_imaging_preparation_protocol_titles') "
                "must be present — an entry with no overrides has no effect."
            )

        if has_pattern:
            _validate_regex(self.specimen_id_pattern, "specimen_groups.specimen_id_pattern")

        return self


# ---------------------------------------------------------------------------
# Dataset-level modification models
# ---------------------------------------------------------------------------

class DatasetAssociations(ClosedBaseModel):
    """
    Explicit REMBI associations for a dataset, expressed as lists of entity
    titles. These are resolved to @id references and written to the Dataset
    entity in the RO-Crate metadata graph.

    All fields are optional — include only those that apply to this dataset.
    The referenced entities must be declared in the top-level rembis block
    (or already exist in the minimal RO-Crate).

    Used for REMBI associations, and optionally alongside 
    image assignment and specimen tracks.
    """
    biosample_titles: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )
    image_acquisition_protocol_titles: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )
    specimen_imaging_preparation_protocol_titles: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )
    annotation_method_titles: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )
    protocol_titles: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )
    image_analysis_method_titles: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )
    image_correlation_method_titles: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )


class ImageAssignmentConfig(ClosedBaseModel):
    """
    Configuration for marking files within a dataset as images.

    Two mutually exclusive forms:

    patterns
        A flat list of glob patterns. All matched files are assigned the
        non-track-aware type 'image'. Typical for Scenario 1.

        In YAML, provide a bare list directly under the 'images:' key:

            images:
              - "**/*.tif"
              - "**/*.ome.tiff"

    by_type
        A dict keyed by image type. Valid keys are the ImageType vocabulary
        (frames, tilt_series, aligned_tilt_series, tomogram, denoised_tomogram)
        plus 'image' for files that are images but do not belong to a specimen
        track. 

            images:
              by_type:
                tilt_series: "**/*.mrc.st"
                tomogram:
                  - "**/*.rec.mrc"
                  - "**/*.mrc"
    """
    patterns: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )
    by_type: dict[str, str | list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_form(self) -> Self:
        has_patterns = bool(self.patterns)
        has_by_type = bool(self.by_type)

        if has_patterns and has_by_type:
            raise ValueError(
                "images: only one of 'patterns' or 'by_type' may be provided."
            )
        if not has_patterns and not has_by_type:
            raise ValueError(
                "images: one of 'patterns' or 'by_type' must be provided."
            )

        if has_by_type:
            bad_keys = set(self.by_type) - _VALID_BY_TYPE_KEYS
            if bad_keys:
                raise ValueError(
                    f"images.by_type: unknown key(s) {sorted(bad_keys)}. "
                    f"Valid keys: {sorted(_VALID_BY_TYPE_KEYS)}"
                )

        return self


class AdditionalFileImageAssignment(ClosedBaseModel):
    """
    Marks a subset of additionally-assigned files as images, with an optional
    image type for specimen track participation.

    patterns
        Glob patterns identifying which of the additionally-assigned files are
        images. Must be a subset of (or equal to) the patterns in the enclosing
        AdditionalFilesConfig.

    image_type
        Optional ImageType value (e.g. 'tilt_series', 'tomogram'). When set,
        the file participates in specimen track identification using this type.
        When absent (or 'image'), the file is a plain image with no track stage.
    """
    patterns: Annotated[list[str], BeforeValidator(_string_to_list)]
    image_type: str | None = None

    @model_validator(mode="after")
    def validate_image_type(self) -> Self:
        if self.image_type is not None and self.image_type not in _VALID_BY_TYPE_KEYS:
            raise ValueError(
                f"additional_files.images: unknown image_type '{self.image_type}'. "
                f"Valid values: {sorted(_VALID_BY_TYPE_KEYS)}"
            )
        return self


class AdditionalFilesConfig(ClosedBaseModel):
    """
    Configuration for assigning currently-unassigned files to an existing named
    dataset, with optional image marking. Files already assigned to any dataset
    are never re-assigned.

    data_directories
        Optional list of directory prefixes. When present, only unassigned files
        whose path falls under one of these directories are considered. Supports
        the same glob syntax as patterns.

    patterns
        Optional glob patterns applied within the candidate pool (after
        data_directories filtering). When absent, all candidates in the
        data_directories are assigned.

    images
        Optional list of image assignment entries. Each entry provides glob
        patterns (a subset of those matched above) and an optional image_type.
        Entries with a typed image_type participate in specimen track
        identification.

    At least one of data_directories or patterns must be provided.
    """
    data_directories: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )
    patterns: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )
    images: list[AdditionalFileImageAssignment] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_has_filter(self) -> Self:
        if not self.data_directories and not self.patterns:
            raise ValueError(
                "additional_files: at least one of 'data_directories' or 'patterns' "
                "must be provided to identify which files to assign."
            )
        return self


class ImageGroupConfig(ClosedBaseModel):
    """
    A named group of track-less images within a dataset, used to assign
    protocol associations at sub-dataset granularity.

    Useful when a dataset contains multiple types of plain (non-track-stage)
    images that require different protocol associations — for example, two
    distinct imaging modalities whose files live in the same dataset.

    patterns
        Glob patterns identifying which image files in this dataset belong to
        this group. Matched files must already be assigned as images (via
        the images block or additional_files).

    protocol_titles
        Titles of Protocol entities to associate with matched image files,
        written to the associated_protocol column in the file list.
    """
    patterns: Annotated[list[str], BeforeValidator(_string_to_list)]
    protocol_titles: Annotated[list[str], BeforeValidator(_string_to_list)] = Field(
        default_factory=list
    )

    @model_validator(mode="after")
    def validate_has_effect(self) -> Self:
        if not self.protocol_titles:
            raise ValueError(
                "image_groups entry: 'protocol_titles' must be non-empty — "
                "an entry with no protocol assignments has no effect."
            )
        return self


class SpecimenTrackAssignmentConfig(ClosedBaseModel):
    """
    Per-dataset configuration for the specimen track scenario.
    Provides IAP/protocol title assignments keyed by image type or 'dataset',
    and per-specimen metadata overrides for this dataset. The cross-dataset
    ID extraction strategy is provided by the top-level specimen_tracks block.

    image_acquisition_protocol_title and protocol_titles are keyed by
    ImageType value (e.g. 'tilt_series', 'tomogram') or 'dataset' for a
    dataset-level assignment — same conventions as in proposal gen.

    Note: dataset-level IAP/protocol associations that do not need to be
    keyed by image type can instead be expressed more simply via the
    DatasetModificationConfig.associations block.
    """
    image_acquisition_protocol_title: dict[str, str | list[str]] | None = None
    protocol_titles: dict[str, str | list[str]] = Field(default_factory=dict)
    specimen_groups: list[SpecimenGroup] = Field(default_factory=list)


class DatasetModificationConfig(ClosedBaseModel):
    """
    Modification instructions for a single named dataset.

    name
        Must match the 'name'/'title' of a dataset already present in the
        minimal RO-Crate.

    associations
        Explicit REMBI associations to write to the Dataset entity. Covers
        all association fields on the Dataset model. Used for modifications
        of REMBIs only, and optionally alongside images/specimen_tracks.

    images
        Glob patterns identifying image files within this dataset. In the
        flat (patterns) form, matched files receive type 'image'. In the
        by_type form, files receive their specific ImageType for track
        identification purposes; all still receive bia:Image in the file list.

    additional_files
        Configuration for assigning currently-unassigned files to this dataset,
        with optional image marking. Runs before images assignment so that
        newly-assigned files are visible to the images block if needed.

    image_groups
        Sub-dataset groups of track-less images, used to assign protocols at
        finer than dataset granularity. Each entry provides glob patterns and
        protocol titles; matched images get protocol associations written to
        the file list.

    specimen_tracks
        Per-dataset IAP/protocol titles keyed by image type, and specimen
        group overrides. Requires the top-level specimen_tracks block
        to be present. For simple (non-type-keyed) associations, prefer
        the associations block instead.
    """
    name: str
    associations: DatasetAssociations | None = Field(None)
    images: ImageAssignmentConfig | None = Field(None)
    additional_files: AdditionalFilesConfig | None = Field(None)
    image_groups: list[ImageGroupConfig] = Field(default_factory=list)
    specimen_tracks: SpecimenTrackAssignmentConfig | None = Field(None)


class ModificationConfig(ClosedBaseModel):
    """
    Top-level modification configuration applied to a minimal RO-Crate.

    rembis
        Study-wide REMBI components to add to the RO-Crate metadata.

    specimen_defaults
        Default biosample/SIPP title references for all specimens discovered
        during track identification. Required when specimen_tracks is present.

    specimen_tracks
        Cross-dataset specimen ID extraction strategy. Must be present if 
        any dataset block defines a specimen_tracks section with
        specimen_groups or by_type image classification.

    datasets
        Per-dataset modification instructions. Names must be unique. A default
        dataset (titled 'Default dataset') is created automatically at the end
        of enrichment for any files that remain unassigned — no explicit entry
        is needed or supported.

    pruning
        Placeholder for future pruning configuration.
    """
    study_metadata: StudyMetadata | None = Field(None)
    rembis: RembiByType | None = Field(None)
    specimen_defaults: SpecimenDefaults | None = Field(None)
    specimen_tracks: SpecimenTrackConfig | None = Field(None)
    datasets: list[DatasetModificationConfig] = Field(default_factory=list)
    pruning: None = Field(None)

    @model_validator(mode="after")
    def validate_dataset_names_unique(self) -> Self:
        names = [d.name for d in self.datasets]
        seen: set[str] = set()
        duplicates = [n for n in names if n in seen or seen.add(n)]
        if duplicates:
            raise ValueError(
                f"Dataset names must be unique; duplicates found: {duplicates}"
            )
        return self

    @model_validator(mode="after")
    def validate_specimen_tracks_consistency(self) -> Self:
        """
        The top-level specimen_tracks block (ID extraction strategy) is
        required only when a dataset block uses specimen_tracks for actual
        track identification — i.e. has specimen_groups or uses by_type image
        classification. A dataset block that only carries IAP/protocol titles
        in specimen_tracks without those features does not require it.

        Additionally, any AdditionalFileImageAssignment with a typed image_type
        (i.e. an ImageType, not 'image') participates in track identification
        and therefore also requires the top-level specimen_tracks block.
        """
        def _needs_top_level_tracks(d: DatasetModificationConfig) -> bool:
            if d.specimen_tracks is not None:
                has_groups = bool(d.specimen_tracks.specimen_groups)
                has_by_type = d.images is not None and bool(d.images.by_type)
                if has_groups or has_by_type:
                    return True

            if d.additional_files is not None:
                typed_images = [
                    img for img in d.additional_files.images
                    if img.image_type is not None and img.image_type != IMAGE_ASSIGNMENT_TYPE_KEY
                ]
                if typed_images:
                    return True

            return False

        if any(_needs_top_level_tracks(d) for d in self.datasets) and self.specimen_tracks is None:
            raise ValueError(
                "One or more datasets use specimen track identification "
                "(specimen_groups, by_type image classification, or typed additional_files images), "
                "but the top-level 'specimen_tracks' (ID extraction strategy) is absent. "
                "Provide a top-level 'specimen_tracks' block."
            )
        return self

    @model_validator(mode="after")
    def validate_specimen_defaults_present(self) -> Self:
        if self.specimen_tracks is None:
            return self
        if self.specimen_defaults is None:
            raise ValueError(
                "A 'specimen_tracks' block is present but 'specimen_defaults' is absent. "
                "Provide a 'specimen_defaults' block with 'biosample_title' and "
                "'specimen_imaging_preparation_protocol_titles'."
            )
        if self.specimen_defaults.biosample_title is None:
            raise ValueError(
                "A 'specimen_tracks' block is present but "
                "'specimen_defaults.biosample_title' is not set. "
                "A biosample title is required for specimen entity creation."
            )
        if not self.specimen_defaults.specimen_imaging_preparation_protocol_titles:
            raise ValueError(
                "A 'specimen_tracks' block is present but "
                "'specimen_defaults.specimen_imaging_preparation_protocol_titles' is empty. "
                "At least one SIPP title is required for specimen entity creation."
            )
        return self
