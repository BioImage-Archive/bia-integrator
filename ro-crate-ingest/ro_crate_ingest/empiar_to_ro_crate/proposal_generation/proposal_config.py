from __future__ import annotations

import re

from pydantic import BaseModel, Field, model_validator

from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.image_tracks import ImageType


_VALID_IMAGE_TYPE_KEYS: frozenset[str] = frozenset(t.value for t in ImageType)
_VALID_IAP_KEYS: frozenset[str] = _VALID_IMAGE_TYPE_KEYS | {"dataset"}


def _validate_regex(pattern: str, location: str) -> None:
    try:
        re.compile(pattern)
    except re.error as exc:
        raise ValueError(f"{location}: invalid regex '{pattern}': {exc}") from exc


def _validate_regex_has_capture_group(pattern: str, location: str) -> None:
    _validate_regex(pattern, location)
    # Permit any capturing group — reject only if there are none at all.
    if not re.search(r'\((?!\?(?::|!|=|<!|<=))', pattern):
        raise ValueError(
            f"{location}: regex '{pattern}' has no capturing group. "
            "Specimen ID extraction requires at least one."
        )


class SpecimenConfig(BaseModel):
    """
    Onle one of the three identification strategies may be non-empty.

    patterns
        Simple regex list. Each pattern must contain at least one capture group.

    pattern_alias_mappings
        Dict mapping a canonical regex pattern to a list of alias patterns.
        The canonical pattern must contain a \\d{N} group so the
        zero-padding transformation can be applied.

    literal_alias_mappings
        Dict mapping a canonical specimen ID string to a list of glob aliases.
    """

    patterns: list[str] = Field(default_factory=list)
    pattern_alias_mappings: dict[str, list[str]] = Field(default_factory=dict)
    literal_alias_mappings: dict[str, list[str]] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_strategies(self) -> SpecimenConfig:
        active = sum([
            bool(self.patterns),
            bool(self.pattern_alias_mappings),
            bool(self.literal_alias_mappings),
        ])
        if active > 1:
            raise ValueError(
                "specimens: only one of 'patterns', 'pattern_alias_mappings', or "
                "'literal_alias_mappings' may be non-empty."
            )

        for i, pattern in enumerate(self.patterns):
            _validate_regex_has_capture_group(pattern, f"specimens.patterns[{i}]")

        for canonical, aliases in self.pattern_alias_mappings.items():
            _validate_regex_has_capture_group(
                canonical, f"specimens.pattern_alias_mappings key '{canonical}'"
            )
            if not re.search(r'\\d\{\d+\}', canonical):
                raise ValueError(
                    f"specimens.pattern_alias_mappings: canonical pattern '{canonical}' "
                    r"must contain a \d{N} group for zero-padding transformation."
                )
            for j, alias in enumerate(aliases):
                _validate_regex_has_capture_group(
                    alias,
                    f"specimens.pattern_alias_mappings['{canonical}'][{j}]",
                )

        return self


class SpecimenDefaults(BaseModel):
    biosample_title: str | None = None
    specimen_imaging_preparation_protocol_titles: list[str] = Field(default_factory=list)


class SpecimenGroup(BaseModel):
    """
    Per-dataset specimen metadata override.

    Just one of ``specimen_ids`` or ``specimen_id_pattern`` must be set.
    At least one metadata override field must be present (otherwise the entry
    has no effect and is likely a mistake).
    """

    specimen_ids: list[str] = Field(default_factory=list)
    specimen_id_pattern: str | None = None
    biosample_title: str | None = None
    specimen_imaging_preparation_protocol_titles: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_group(self) -> SpecimenGroup:
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
                "must be provided — an entry with no overrides has no effect."
            )

        if has_pattern:
            _validate_regex(
                self.specimen_id_pattern,
                "specimen_groups.specimen_id_pattern",
            )

        return self


class DatasetConfig(BaseModel):
    """
    One entry from the ``datasets`` list in the proposal config.
    Keys for ``file_globs``, ``image_acquisition_protocol_title``, and ``protocol_titles`` 
    are checked against valid image types.
    """

    name: str
    data_directories: str | list[str]
    file_globs: dict[str, str | list[str]] = Field(default_factory=dict)
    image_acquisition_protocol_title: dict[str, str | list[str]] | None = None
    protocol_titles: dict[str, str | list[str]] = Field(default_factory=dict)
    specimen_groups: list[SpecimenGroup] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_keys(self) -> DatasetConfig:
        if self.image_acquisition_protocol_title:
            bad_iap_keys = set(self.image_acquisition_protocol_title) - _VALID_IAP_KEYS
            if bad_iap_keys:
                raise ValueError(
                    f"Dataset '{self.name}': unknown image_acquisition_protocol_title "
                    f"key(s): {bad_iap_keys}. Valid keys: {sorted(_VALID_IAP_KEYS)}"
                )

        bad_pt_keys = set(self.protocol_titles) - _VALID_IMAGE_TYPE_KEYS
        if bad_pt_keys:
            raise ValueError(
                f"Dataset '{self.name}': unknown protocol_titles key(s): {bad_pt_keys}. "
                f"Valid keys: {sorted(_VALID_IMAGE_TYPE_KEYS)}"
            )

        bad_fg_keys = set(self.file_globs) - _VALID_IMAGE_TYPE_KEYS
        if bad_fg_keys:
            raise ValueError(
                f"Dataset '{self.name}': unknown file_globs key(s): {bad_fg_keys}. "
                f"Valid keys: {sorted(_VALID_IMAGE_TYPE_KEYS)}"
            )

        return self


class ProposalConfig(BaseModel):
    accession_id: str
    paper_doi: str | None = None
    pattern_inference_delimiters: list[str] = Field(default_factory=lambda: ["_", "."])
    specimens: SpecimenConfig = Field(default_factory=SpecimenConfig)
    specimen_defaults: SpecimenDefaults | None = None
    datasets: list[DatasetConfig] = Field(default_factory=list)
    
    biosamples: list[dict] = Field(default_factory=list)
    specimen_imaging_preparation_protocols: list[dict] = Field(default_factory=list)
    image_acquisition_protocols: list[dict] = Field(default_factory=list)
    protocols: list[dict] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_dataset_names_unique(self) -> ProposalConfig:
        names = [d.name for d in self.datasets]
        seen: set[str] = set()
        dupes = [n for n in names if n in seen or seen.add(n)] 
        if dupes:
            raise ValueError(
                f"Dataset names must be unique; duplicates found: {dupes}"
            )
        return self
