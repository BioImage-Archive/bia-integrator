import glob
import logging
import pandas as pd
import re
from pathlib import Path
from pydantic import BaseModel, computed_field, Field

from ro_crate_ingest.empiar_to_ro_crate.empiar.file_api import EMPIARFile
from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.image_types import ImageType
from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.proposal_config import (
    DatasetConfig,
    SpecimenConfig,
)

logger = logging.getLogger(__name__)


class ImageTrack(BaseModel):
    """
    ImageTrack represents one complete experimental unit: the track from
    raw movie frames through the tilt series to a reconstructed tomogram,
    all belonging to a single specimen.

    dataset_for maps each ImageType value (str) to the name of the dataset
    block that contributed that image type. extra_files has no entry in
    dataset_for since their provenance is not meaningful for downstream use.
    """
    specimen_id: str
    frames: list[Path] = Field(default_factory=list)
    tilt_series: Path | None = None
    aligned_tilt_series: Path | None = None
    tomogram: Path | None = None
    denoised_tomogram: Path | None = None
    extra_files: list[Path] = Field(default_factory=list)
    dataset_for: dict[str, str] = Field(default_factory=dict)

    @computed_field
    @property
    def track_start(self) -> ImageType:
        if self.frames:
            return ImageType.FRAMES
        if self.tilt_series is not None:
            return ImageType.TILT_SERIES
        if self.aligned_tilt_series is not None:
            return ImageType.ALIGNED_TILT_SERIES
        if self.tomogram is not None:
            return ImageType.TOMOGRAM
        if self.denoised_tomogram is not None:
            return ImageType.DENOISED_TOMOGRAM
        raise ValueError(f"ImageTrack for specimen '{self.specimen_id}' has no images")


def _extract_specimen_id(
    file_path: Path,
    specimen_config: "SpecimenConfig",
) -> str | None:
    """
    Extract specimen ID using one of three methods:

    1. patterns: list[str] - simple regex patterns
    2. pattern_alias_mappings: dict[str, list[str]] - canonical pattern -> alias patterns
       (with algorithmic transformation, e.g., zero-padding)
    3. literal_alias_mappings: dict[str, list[str]] - canonical_id -> [literal_aliases]
       (direct, or with globs, lookup table for arbitrary relationships)
    """
    path_str = file_path.as_posix()

    # Case 1: Simple patterns
    for pattern in specimen_config.patterns:
        match = re.search(pattern, path_str)
        if match:
            groups = [g for g in match.groups() if g is not None]
            if len(groups) > 1:
                return "_".join(groups)
            return groups[0]

    # Case 2: Pattern alias mappings (with transformation)
    for canonical_pattern, alias_patterns in specimen_config.pattern_alias_mappings.items():
        for alias_pattern in alias_patterns:
            match = re.search(alias_pattern, path_str)
            if match:
                raw_id = match.group(1)
                return _transform_to_canonical_id(raw_id, canonical_pattern)

    # Case 3: Literal alias mappings (glob matching with ** support)
    for canonical_id, aliases in specimen_config.literal_alias_mappings.items():
        for alias in aliases:
            regex_pattern = glob.translate(alias, recursive=True, include_hidden=True)
            if re.match(regex_pattern, path_str):
                return canonical_id

    return None


def _transform_to_canonical_id(raw_id: str, canonical_pattern: str) -> str:
    """
    Transform a raw specimen ID to match the canonical pattern format.
    For example: "12" with pattern "(\\d{4})" -> "0012"
    """
    digit_length_match = re.search(r'\\d\{(\d+)\}', canonical_pattern)
    if digit_length_match:
        target_length = int(digit_length_match.group(1))
        if raw_id.isdigit():
            return raw_id.zfill(target_length)
    return raw_id


def _match_any_pattern(path: Path, patterns: str | list[str]) -> bool:
    """Return True if path matches any of the given glob patterns."""
    if isinstance(patterns, str):
        patterns = [patterns]
    return any(path.match(pattern) for pattern in patterns)


def _classify_file(
    path: Path,
    file_type_patterns: dict[str, str | list[str]],
    dataset_name: str,
) -> ImageType | None:
    """
    Classify a file against the type patterns defined for a dataset.

    Returns the matching ImageType, or None if no pattern matches.
    Gives a warning (and returns first match) if the file matches more than
    one type — that situation indicates a misconfigured pattern set.
    """
    matched: list[ImageType] = []
    for type_name, glob_patterns in file_type_patterns.items():
        if _match_any_pattern(path, glob_patterns):
            try:
                matched.append(ImageType(type_name))
            except ValueError:
                logger.warning(
                    f"Dataset '{dataset_name}': pattern key '{type_name}' does "
                    f"not correspond to a known ImageType and will be ignored."
                )
                break

    if len(matched) > 1:
        logger.warning(
            f"Dataset '{dataset_name}': '{path}' matched multiple image types "
            f"{[t.value for t in matched]}; assigning the first ({matched[0].value})."
        )

    return matched[0] if matched else None


def _rate_dataset_specificity(data_directories: list[str]) -> int:
    """
    Return a specificity score for a dataset, defined as the maximum
    number of '/' separators across its data_directories. Used to break ties
    when multiple dataset blocks claim the same file: the deeper directory wins.
    """
    return max((d.count("/") for d in data_directories), default=0)


def _build_file_dataframe(
    files: list[EMPIARFile],
    datasets_config: "list[DatasetConfig]",
    specimen_config: "SpecimenConfig",
) -> pd.DataFrame:
    """
    Builds a one-row-per-file DataFrame covering all datasets.

    DataFrame columns:
        path          : Path
        size_in_bytes : int
        dataset_name  : str        -- name of the winning (see below) dataset block
        specimen_id   : str | NaN  -- extracted from path; NaN if unmatched
        image_type    : str | NaN  -- ImageType.value, or NaN if unclassified

    Resolution when multiple dataset blocks claim the same file:
      1. A dataset that assigns an image_type beats one that does not.
      2. Among ties on (1), the block with the deepest data_directory
         (most '/' separators) wins.
      3. Any remaining tie is broken by order in datasets_config (first wins).

    Note that points 2 and 3 above are somewhat moot, since we are interested in
    assigned image files, thus the allocation of files not assigned is not critical.
    Files not claimed by any dataset block are omitted entirely.
    """
    base_df = pd.DataFrame(
        [{"path": Path(f.path), "size_in_bytes": f.size_in_bytes} for f in files]
    )

    candidate_rows: list[pd.DataFrame] = []

    for dataset_config in datasets_config:
        dataset_name = dataset_config.name

        data_dirs = dataset_config.data_directories

        dir_mask = pd.Series(False, index=base_df.index)
        for data_dir in data_dirs:
            dir_mask |= base_df["path"].astype(str).str.startswith(data_dir)

        subset = base_df[dir_mask].copy()
        if subset.empty:
            logger.warning(
                f"Dataset '{dataset_name}': no files matched "
                f"data_directories {data_dirs}. Check directory paths."
            )
            continue

        subset["specimen_id"] = subset["path"].apply(
            lambda p: _extract_specimen_id(p, specimen_config)
        )

        unmatched_mask = subset["specimen_id"].isna()
        if unmatched_mask.any():
            unmatched_paths = subset.loc[unmatched_mask, "path"].tolist()
            logger.warning(
                f"Dataset '{dataset_name}': {len(unmatched_paths)} file(s) could not "
                "be assigned a specimen ID and will be skipped."
            )
            logger.debug("Files not assigned specimen ID: \n" 
                + "\n".join(f"  {p}" for p in unmatched_paths))
        subset = subset.dropna(subset=["specimen_id"])

        subset["image_type"] = subset["path"].apply(
            lambda p: (
                t.value
                if (t := _classify_file(p, dataset_config.file_globs, dataset_name))
                else None
            )
        )

        subset["dataset_name"] = dataset_name
        subset["_specificity"] = _rate_dataset_specificity(data_dirs)

        candidate_rows.append(subset)

    if not candidate_rows:
        return pd.DataFrame(
            columns=["path", "size_in_bytes", "dataset_name", "specimen_id", "image_type"]
        )

    candidates = pd.concat(candidate_rows, ignore_index=True)

    # Encode dataset precedence as sortable columns: typed rows first, deeper dirs first.
    candidates["_has_type"] = candidates["image_type"].notna().astype(int)
    candidates = candidates.sort_values(
        ["_has_type", "_specificity"],
        ascending=[False, False],
        kind="stable",
    )

    resolved = (
        candidates
        .drop_duplicates(subset=["path"], keep="first")
        .drop(columns=["_has_type", "_specificity"])
        .reset_index(drop=True)
    )

    claim_counts = candidates.groupby("path")["dataset_name"].nunique()
    contested_paths = claim_counts[claim_counts > 1].index
    if not contested_paths.empty:
        if logger.isEnabledFor(logging.DEBUG):
            for path in contested_paths:
                claimants = candidates.loc[candidates["path"] == path, "dataset_name"].tolist()
                winner = resolved.loc[resolved["path"] == path, "dataset_name"].iloc[0]
                logger.debug(
                    f"File '{path}' claimed by multiple dataset blocks "
                    f"{claimants}; assigned to '{winner}'."
                )
        else:
            logger.warning(
                f"{len(contested_paths)} file(s) were claimed by multiple datasets. "
                "Enable DEBUG logging for details."
            )

    return resolved


def _merge_tracks(df: pd.DataFrame) -> list[ImageTrack]:
    """
    Make one ImageTrack per specimen_id from the per-row DataFrame.

    _build_file_dataframe guarantees one row per file, so there is no
    deduplication to do here — accumulate into track fields and
    record dataset provenance in dataset_for.
    """
    tracks: dict[str, ImageTrack] = {}

    for _, row in df.iterrows():
        sid = str(row["specimen_id"])
        path = row["path"]
        image_type = row["image_type"]
        dataset_name = row["dataset_name"]

        if str(path).startswith("data/"):
            path = Path(path.relative_to("data/"))

        track = tracks.setdefault(sid, ImageTrack(specimen_id=sid))

        if pd.isna(image_type):
            track.extra_files.append(path)
            continue

        if image_type == ImageType.FRAMES:
            track.frames.append(path)
            track.dataset_for[ImageType.FRAMES] = dataset_name

        # TODO: even/odd tilt series images
        elif image_type == ImageType.TILT_SERIES:
            if track.tilt_series is not None:
                logger.warning(
                    f"Specimen {sid}: second tilt series file encountered "
                    f"('{path}'); keeping the first."
                )
            else:
                track.tilt_series = path
                track.dataset_for[ImageType.TILT_SERIES] = dataset_name

        elif image_type == ImageType.ALIGNED_TILT_SERIES:
            if track.aligned_tilt_series is not None:
                logger.warning(
                    f"Specimen {sid}: second aligned tilt series file "
                    f"encountered ('{path}'); keeping the first."
                )
            else:
                track.aligned_tilt_series = path
                track.dataset_for[ImageType.ALIGNED_TILT_SERIES] = dataset_name

        elif image_type == ImageType.TOMOGRAM:
            if track.tomogram is not None:
                logger.warning(
                    f"Specimen {sid}: second tomogram file encountered "
                    f"('{path}'); keeping the first."
                )
            else:
                track.tomogram = path
                track.dataset_for[ImageType.TOMOGRAM] = dataset_name

        elif image_type == ImageType.DENOISED_TOMOGRAM:
            if track.denoised_tomogram is not None:
                logger.warning(
                    f"Specimen {sid}: second denoised tomogram file "
                    f"encountered ('{path}'); keeping the first."
                )
            else:
                track.denoised_tomogram = path
                track.dataset_for[ImageType.DENOISED_TOMOGRAM] = dataset_name
        
        else:
            logger.warning(
                f"Specimen {sid}: unrecognised image type '{image_type}' for "
                f"'{path}'; file will be skipped."
            )

    for track in tracks.values():
        track.frames.sort()
        track.extra_files.sort()

    return sorted(tracks.values(), key=lambda t: t.specimen_id)


def identify_tracks(
    files: list[EMPIARFile],
    datasets_config: "list[DatasetConfig]",
    specimen_config: "SpecimenConfig",
) -> list[ImageTrack]:
    """
    Build one ImageTrack per specimen by processing all dataset config blocks
    together and merging contributions from each.

    Args ---
        files:
            Full file listing for the EMPIAR entry.
        datasets_config:
            The validated list of DatasetConfig objects from the proposal config.
        specimen_config:
            The validated SpecimenConfig from the proposal config.

    Returns ---
        list[ImageTrack]
            One track per specimen_id, sorted alphabetically. Tracks may be
            incomplete (missing frames / tilt_series / tomogram) if the
            corresponding dataset blocks did not cover that specimen; use
            `validate_tracks` for a completeness report.
    """
    df = _build_file_dataframe(files, datasets_config, specimen_config)

    if df.empty:
        logger.warning("No files could be classified across any dataset block.")
        return []

    tracks = _merge_tracks(df)

    logger.info(
        f"Identified {len(tracks)} unique specimen track(s) across "
        f"{len(datasets_config)} dataset block(s)."
    )
    return tracks


def validate_tracks(
    tracks: list[ImageTrack],
    files: list[EMPIARFile],
) -> dict:
    """
    Report on track completeness and any files not assigned to any track.

    A track is considered complete if it has frames, a tilt series, and a
    tomogram. Each incomplete track entry lists which stages are absent (in debug).
    """
    all_tracked: set[Path] = set()
    for track in tracks:
        all_tracked.update(track.frames)
        all_tracked.update(track.extra_files)
        for attr in ("tilt_series", "aligned_tilt_series", "tomogram", "denoised_tomogram"):
            val = getattr(track, attr)
            if val is not None:
                all_tracked.add(val)

    all_paths = {Path(f.path).relative_to("data/") for f in files}
    orphaned = sorted(all_paths - all_tracked)

    incomplete: list[dict] = []
    for track in tracks:
        missing = []
        if not track.frames:
            missing.append("frames")
        if track.tilt_series is None:
            missing.append("tilt_series")
        if track.tomogram is None:
            missing.append("tomogram")
        if missing:
            incomplete.append({"specimen_id": track.specimen_id, "missing": missing})
            logger.debug(
                f"Incomplete track for specimen {track.specimen_id}: missing {missing}."
            )

    return {
        "total_tracks": len(tracks),
        "complete_tracks": len(tracks) - len(incomplete),
        "incomplete_tracks": incomplete,
        "orphaned_file_count": len(orphaned),
        "orphaned_files": orphaned,
        "coverage": len(all_tracked) / len(all_paths) if all_paths else 0.0,
    }
