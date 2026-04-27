import glob
import logging
import pandas as pd
import re
from pathlib import Path
from pydantic import BaseModel, computed_field, Field

from bia_ro_crate.models import ro_crate_models
from bia_ro_crate.models.linked_data.ontology_terms import BIA
from bia_ro_crate.models.linked_data.pydantic_ld.LDModel import ObjectReference
from bia_ro_crate.core.bia_ro_crate_metadata import BIAROCrateMetadata
from bia_ro_crate.core.file_list import FileList
from ro_crate_ingest.ro_crate_modification.enrichment.image_types import ImageType
from ro_crate_ingest.ro_crate_modification.enrichment.file_list_utils import (
    RDF_TYPE_PROPERTY,
    get_dataset_column_id,
    get_or_add_associated_source_image_column_id,
    get_or_add_associated_subject_column_id,
    get_path_column_id,
)
from ro_crate_ingest.ro_crate_modification.enrichment.utils import (
    FILE_TYPE_IMAGE,
    match_patterns,
    ref,
    resolve_dataset_id_by_name,
    title_to_id,
    type_for,
)
from ro_crate_ingest.ro_crate_modification.modification_config import (
    IMAGE_ASSIGNMENT_TYPE_KEY,
    AdditionalFilesConfig,
    DatasetModificationConfig,
    ModificationConfig,
    SpecimenDefaults,
    SpecimenGroup,
    SpecimenTrackConfig,
)

logger = logging.getLogger(__name__)


_FRAME_LABEL_DELIMITERS = ["_", "."]


class SpecimenTrack(BaseModel):
    """
    SpecimenTrack represents one complete experimental unit of images,
    linked by a specimen.
    
    For example in cryoET — the track from raw movie frames through the 
    tilt series to a reconstructed tomogram, all belonging to one specimen.

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


def _classify_file_by_type(
    path: Path,
    by_type: dict[str, str | list[str]],
    dataset_name: str,
) -> str | None:
    """
    Classify a file against the by_type patterns from an ImageAssignmentConfig.
    Returns the matching ImageType value string, or None if no pattern matches
    or if the key is the plain 'image' sentinel (which is not a track stage).
    """
    matched: list[str] = []
    for type_key, raw_patterns in by_type.items():
        patterns = [raw_patterns] if isinstance(raw_patterns, str) else raw_patterns
        if match_patterns(str(path), patterns):
            matched.append(type_key)

    if len(matched) > 1:
        logger.warning(
            f"Dataset '{dataset_name}': '{path}' matched multiple by_type keys "
            f"{matched}; using first ({matched[0]})."
        )

    if not matched:
        return None

    key = matched[0]
    # The plain 'image' key marks a file as an image without track stage
    # membership — return None so _merge_tracks treats it as an extra_file.
    if key == IMAGE_ASSIGNMENT_TYPE_KEY:
        return None

    return key


def _classify_file_by_additional_images(
    path: Path,
    additional_files: AdditionalFilesConfig,
    dataset_name: str,
) -> str | None:
    """
    Classify a file against the typed image assignments in an AdditionalFilesConfig.
    Returns the image_type string for the first matching entry whose image_type is
    a real ImageType (not the plain 'image' sentinel), or None if no typed entry
    matches (treating it as a non-track-stage image).

    Entries with image_type=None or image_type='image' are skipped here — those
    files are plain images that do not participate in specimen track identification.
    """
    matched_typed: list[str] = []
    for img_assignment in additional_files.images:
        if img_assignment.image_type is None or img_assignment.image_type == IMAGE_ASSIGNMENT_TYPE_KEY:
            continue
        if match_patterns(str(path), img_assignment.patterns):
            matched_typed.append(img_assignment.image_type)

    if len(matched_typed) > 1:
        logger.warning(
            f"Dataset '{dataset_name}': '{path}' matched multiple typed additional_files "
            f"image entries {matched_typed}; using first ({matched_typed[0]})."
        )

    return matched_typed[0] if matched_typed else None


def _extract_specimen_id(
    file_path: Path,
    specimen_config: SpecimenTrackConfig,
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


def _build_track_dataframe(
    file_list: FileList,
    ro_crate_metadata: BIAROCrateMetadata,
    dataset_configs_for_tracks: list[DatasetModificationConfig],
    specimen_track_config: SpecimenTrackConfig,
) -> pd.DataFrame:
    """
    Build a one-row-per-file DataFrame for _merge_tracks, reading from the
    file list.

    For each dataset that participates in specimen track identification —
    either via images.by_type or via typed entries in additional_files.images:
      - Filter file list to image-assigned rows belonging to that dataset
      - Classify each file as an ImageType using whichever source applies
      - Extract a specimen ID from each file path using specimen_track_config

    Classification sources (mutually exclusive per dataset):
      - images.by_type: classic glob-keyed dict, handled by _classify_file_by_type
      - additional_files.images typed entries: handled by _classify_file_by_additional_images

    Result columns: path, dataset_name, specimen_id, image_type
    """
    path_col_id = get_path_column_id(file_list)
    type_col_id = file_list.get_column_id_by_property(RDF_TYPE_PROPERTY)
    dataset_col_id = get_dataset_column_id(file_list)

    if path_col_id is None or dataset_col_id is None:
        raise ValueError(
            "Specimen track identification requires both a file path column and a "
            "dataset membership column in the file list. One or both are absent."
        )

    candidate_rows: list[pd.DataFrame] = []

    for dataset_config in dataset_configs_for_tracks:
        dataset_id = resolve_dataset_id_by_name(ro_crate_metadata, dataset_config.name)
        if dataset_id is None:
            continue

        # Image-assigned rows belonging to this dataset
        type_series = file_list.data.get(type_col_id, pd.Series(dtype=str))
        image_mask = (
            (file_list.data[dataset_col_id] == dataset_id)
            & (type_series == FILE_TYPE_IMAGE)
        )
        subset = file_list.data[image_mask][[path_col_id]].copy()
        subset = subset.rename(columns={path_col_id: "path"})
        subset["path"] = subset["path"].apply(Path)

        if subset.empty:
            logger.warning(
                f"Dataset '{dataset_config.name}': no image-assigned files found "
                "for specimen track identification."
            )
            continue

        # Classify each file by ImageType.
        # For images.by_type datasets: use the by_type glob dict.
        # For additional_files typed image datasets: use the typed image entries.
        # Files that resolve to no typed stage get image_type = None and are
        # treated as extra_files in the track (no label/specimen written).
        has_by_type = dataset_config.images is not None and bool(dataset_config.images.by_type)
        if has_by_type:
            subset["image_type"] = subset["path"].apply(
                lambda p: _classify_file_by_type(
                    p, dataset_config.images.by_type, dataset_config.name
                )
            )
        else:
            # additional_files with typed image entries
            subset["image_type"] = subset["path"].apply(
                lambda p: _classify_file_by_additional_images(
                    p, dataset_config.additional_files, dataset_config.name
                )
            )

        # Extract specimen ID from path using the cross-dataset strategy
        subset["specimen_id"] = subset["path"].apply(
            lambda p: _extract_specimen_id(p, specimen_track_config)
        )

        unmatched = subset["specimen_id"].isna().sum()
        if unmatched:
            logger.warning(
                f"Dataset '{dataset_config.name}': {unmatched} file(s) could not be "
                "assigned a specimen ID and will be skipped."
            )
        subset = subset.dropna(subset=["specimen_id"])

        subset["dataset_name"] = dataset_config.name
        candidate_rows.append(subset[["path", "dataset_name", "specimen_id", "image_type"]])

    if not candidate_rows:
        return pd.DataFrame(columns=["path", "dataset_name", "specimen_id", "image_type"])

    return pd.concat(candidate_rows, ignore_index=True)



def _merge_tracks(df: pd.DataFrame) -> list[SpecimenTrack]:
    """
    Make one ImageTrack per specimen_id from the per-row DataFrame.

    _build_file_dataframe guarantees one row per file, so there is no
    deduplication to do here — accumulate into track fields and
    record dataset provenance in dataset_for.
    """
    tracks: dict[str, SpecimenTrack] = {}

    for _, row in df.iterrows():
        sid = str(row["specimen_id"])
        path = row["path"]
        image_type = row["image_type"]
        dataset_name = row["dataset_name"]

        track = tracks.setdefault(sid, SpecimenTrack(specimen_id=sid))

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


def _resolve_specimen_metadata(
    tracks: list[SpecimenTrack],
    specimen_defaults: SpecimenDefaults | None,
    dataset_configs_with_additional_specimen_data: list[DatasetModificationConfig],
) -> list[dict]:
    """
    Build per-specimen metadata dicts from tracks, applying the same
    defaults -> specimen_groups cascade as the proposal generation path.

    Returns a list of dicts with keys:
        title, biosample_title, specimen_imaging_preparation_protocol_titles
    """
    group_lookup: dict[str, SpecimenGroup] = {}
    group_patterns: list[tuple[str, SpecimenGroup]] = []

    for dataset_config in dataset_configs_with_additional_specimen_data:
        for group in dataset_config.specimen_tracks.specimen_groups:
            if group.specimen_id_pattern is not None:
                group_patterns.append((group.specimen_id_pattern, group))
            else:
                for sid in group.specimen_ids:
                    group_lookup[sid] = group

    specimens: list[dict] = []
    for track in tracks:
        sid = track.specimen_id

        biosample_title = specimen_defaults.biosample_title if specimen_defaults else None
        sipp_titles = (
            list(specimen_defaults.specimen_imaging_preparation_protocol_titles)
            if specimen_defaults else []
        )

        override: SpecimenGroup | None = group_lookup.get(sid)
        if override is None:
            for pattern, group in group_patterns:
                if re.search(pattern, sid):
                    override = group
                    break

        if override is not None:
            if override.biosample_title is not None:
                biosample_title = override.biosample_title
            if override.specimen_imaging_preparation_protocol_titles:
                sipp_titles = list(override.specimen_imaging_preparation_protocol_titles)

        specimens.append({
            "title": f"Specimen_{sid}",
            "biosample_title": biosample_title,
            "specimen_imaging_preparation_protocol_titles": sipp_titles,
        })

    return specimens


def _make_specimen_entities(
    spec_meta: dict,
) -> ro_crate_models.Specimen:
    """
    Build a Specimen entity from resolved per-specimen metadata.

    Specimen references its BioSample(s) and SIPP(s) by @id.
    """
    title = spec_meta["title"]
    biosample_title = spec_meta["biosample_title"]
    sipp_titles = spec_meta["specimen_imaging_preparation_protocol_titles"]

    biological_entity_refs = [ref(biosample_title)] if biosample_title else []
    sipp_refs = [ref(t) for t in sipp_titles]

    specimen = ro_crate_models.Specimen(**{
        "@id": title_to_id(title),
        "@type": type_for(ro_crate_models.Specimen),
        "biologicalEntity": biological_entity_refs,
        "imagingPreparationProtocol": sipp_refs,
    })

    return specimen


def _apply_dataset_track_metadata(
    ro_crate_metadata: BIAROCrateMetadata,
    dataset_config: DatasetModificationConfig,
    tracks: list[SpecimenTrack],
) -> None:
    """
    Update the Dataset entity in the RO-Crate with IAP and protocol
    associations from the per-dataset specimen_tracks config. These are keyed
    by image type or 'dataset' and are distinct from the simpler flat
    associations in the DatasetAssociations block — both can be present.
    """
    if dataset_config.specimen_tracks is None:
        return

    dataset_id = resolve_dataset_id_by_name(ro_crate_metadata, dataset_config.name)
    if dataset_id is None:
        return

    entity = ro_crate_metadata.get_object(dataset_id)
    if not isinstance(entity, ro_crate_models.Dataset):
        logger.warning(
            f"Entity '{dataset_id}' is not a Dataset; cannot apply track metadata."
        )
        return

    track_config = dataset_config.specimen_tracks

    iap_refs: list[ObjectReference] = []
    if track_config.image_acquisition_protocol_title:
        seen: set[str] = set()
        for titles in track_config.image_acquisition_protocol_title.values():
            for t in ([titles] if isinstance(titles, str) else titles):
                if t not in seen:
                    iap_refs.append(ref(t))
                    seen.add(t)

    protocol_refs: list[ObjectReference] = []
    if track_config.protocol_titles:
        seen = set()
        for titles in track_config.protocol_titles.values():
            for t in ([titles] if isinstance(titles, str) else titles):
                if t not in seen:
                    protocol_refs.append(ref(t))
                    seen.add(t)

    updated = entity.model_copy(update={
        "associatedImageAcquisitionProtocol": (
            list(entity.associatedImageAcquisitionProtocol) + iap_refs
        ),
        "associatedProtocol": (
            list(entity.associatedProtocol) + protocol_refs
        ),
    })
    ro_crate_metadata.update_entity(updated)
    logger.debug(
        f"Dataset '{dataset_config.name}': added {len(iap_refs)} IAP ref(s) "
        f"and {len(protocol_refs)} protocol ref(s) from specimen_tracks config."
    )


def _split_with_delimiters(split_pattern: str, split_string: str) -> list[str]:
    return re.split(split_pattern, split_string)


def _infer_frame_pattern(frame_files: list[Path]) -> str | None:
    """
    Given a list of frame file paths (all from one specimen), infer the
    file pattern by replacing the variable parts with {}.
    """
    if not frame_files:
        return None

    str_paths = [str(p) for p in sorted(frame_files)]
    if len(str_paths) == 1:
        return str_paths[0]

    escaped = [re.escape(d) for d in _FRAME_LABEL_DELIMITERS]
    split_pattern = '(' + '|'.join(escaped) + ')'

    tokenised = [_split_with_delimiters(split_pattern, p) for p in str_paths]

    lengths = {len(t) for t in tokenised}
    if len(lengths) > 1:
        logger.warning(
            "Frame files for a specimen have inconsistent token counts after "
            f"splitting on {_FRAME_LABEL_DELIMITERS}; falling back to first "
            "path as pattern."
        )
        return str_paths[0]

    first_tokens = tokenised[0]
    result_parts = []
    for i, token in enumerate(first_tokens):
        if token in _FRAME_LABEL_DELIMITERS:
            result_parts.append(token)
            continue
        if all(t[i] == token for t in tokenised[1:]):
            result_parts.append(token)
        else:
            result_parts.append('{}')

    return ''.join(result_parts)


def _fill_frame_label(frame_path: Path, pattern: str, label_prefix: str) -> str:
    """
    Given a frame file path and the inferred pattern for its specimen,
    construct a per-frame label by filling the {} slots with the varying
    token values from this file's path, excluding the file extension.

    For example:
        pattern:      "data/frames/20190429/TS_05_{}_{}. 0.tif"
        frame_path:   "data/frames/20190429/TS_05_001_-0.0.tif"
        label_prefix: "Specimen_centrosome_01 frames"
        → "Specimen_centrosome_01 frames_001_-0"
    """
    escaped = [re.escape(d) for d in _FRAME_LABEL_DELIMITERS]
    split_pattern = '(' + '|'.join(escaped) + ')'

    path_str = str(frame_path)
    path_nosuffix = path_str[:path_str.rfind('.')] if '.' in path_str else path_str
    pattern_nosuffix = pattern[:pattern.rfind('.')] if '.' in pattern else pattern
    
    pattern_tokens = _split_with_delimiters(split_pattern, pattern_nosuffix)
    path_tokens = _split_with_delimiters(split_pattern, path_nosuffix)

    if len(pattern_tokens) != len(path_tokens):
        logger.warning(
            f"Token count mismatch between pattern '{pattern}' and path "
            f"'{frame_path}'; using path stem as label suffix."
        )
        return f"{label_prefix}_{frame_path.stem}"

    varying_parts = []
    seen_varying = False
    for pt, vt in zip(pattern_tokens, path_tokens):
        if pt == '{}':
            varying_parts.append(vt)
            seen_varying = True
        elif seen_varying:
            # Append delimiters and constant tokens that follow a varying part
            varying_parts.append(vt)

    if not varying_parts:
        return f"{label_prefix}_{frame_path.stem}"

    # Strip any trailing delimiters
    while varying_parts and varying_parts[-1] in _FRAME_LABEL_DELIMITERS:
        varying_parts.pop()

    return label_prefix + '_' + ''.join(varying_parts)


def _generate_labels(tracks: list[SpecimenTrack]) -> dict[str, str]:
    """
    Build a path -> label mapping for all image files across all tracks.

    Frames: per-file label constructed by filling {} slots in the inferred
    pattern with the varying token values from each frame's path, giving
    e.g. "Specimen_0042 frames_0003_-15.0".

    All other image types: label is "Specimen_{sid} {image_type.value}",
    e.g. "Specimen_0042 tilt_series".

    Returns a dict keyed by str(path) as it appears in the track, matching
    what is stored in the file list.
    """
    path_to_label: dict[str, str] = {}

    for track in tracks:
        sid = track.specimen_id
        label_prefix = f"Specimen_{sid} frames"

        if track.frames:
            pattern = _infer_frame_pattern(track.frames)
            for frame_path in track.frames:
                if pattern is not None:
                    label = _fill_frame_label(frame_path, pattern, label_prefix)
                else:
                    label = f"{label_prefix}_{frame_path.stem}"
                path_to_label[str(frame_path)] = label

        for image_type in [
            ImageType.TILT_SERIES,
            ImageType.ALIGNED_TILT_SERIES,
            ImageType.TOMOGRAM,
            ImageType.DENOISED_TOMOGRAM,
        ]:
            file_path = getattr(track, image_type.value)
            if file_path is not None:
                path_to_label[str(file_path)] = f"Specimen_{sid} {image_type.value}"

    return path_to_label


def _write_label_column(
    file_list: FileList,
    path_to_label: dict[str, str],
) -> None:
    """
    Write the label column for all image files that have a label in
    path_to_label.
    """
    path_col_id = get_path_column_id(file_list)
    if path_col_id is None:
        return

    label_col_id = file_list.get_column_id_by_property("http://schema.org/name")
    if label_col_id is None:
        logger.warning("No label column found in file list; skipping label writing.")
        return
    if file_list.data[label_col_id].dtype != object:
        file_list.data[label_col_id] = file_list.data[label_col_id].astype(object)

    labels = file_list.data[path_col_id].apply(
        lambda p: path_to_label.get(str(p))
    )
    file_list.data[label_col_id] = labels

    written = int(labels.notna().sum())
    logger.info(f"Wrote label for {written} file(s).")


def _write_source_image_labels(
    file_list: FileList,
    tracks: list[SpecimenTrack],
    path_to_label: dict[str, str],
) -> None:
    """
    For each non-track-start image, write the label(s) of its upstream
    image(s) into the source_image_label column.

    For tilt_series whose upstream is frames, the value is a serialised
    list of all frame labels e.g. "['Specimen_0042 frames_0001_-15.0', ...]".
    For all other upstream relationships there is a single upstream file,
    so the value is a plain string.
    """
    path_col_id = get_path_column_id(file_list)
    if path_col_id is None:
        return

    source_label_col_id = get_or_add_associated_source_image_column_id(file_list)
    if file_list.data[source_label_col_id].dtype != object:
        file_list.data[source_label_col_id] = file_list.data[source_label_col_id].astype(object)

    path_to_source_label: dict[str, str] = {}

    for track in tracks:
        frames_labels = (
            [path_to_label[str(p)] for p in track.frames if str(p) in path_to_label]
            if track.frames else []
        )
        frames_source = str(frames_labels) if len(frames_labels) > 1 else (frames_labels[0] if frames_labels else None)

        ts_label = path_to_label.get(str(track.tilt_series)) if track.tilt_series else None
        ats_label = path_to_label.get(str(track.aligned_tilt_series)) if track.aligned_tilt_series else None

        upstream: dict[ImageType, str | None] = {
            ImageType.TILT_SERIES: frames_source,
            ImageType.ALIGNED_TILT_SERIES: ts_label or frames_source,
            ImageType.TOMOGRAM: ats_label or ts_label or frames_source,
            ImageType.DENOISED_TOMOGRAM: ats_label or ts_label or frames_source,
        }

        for image_type, upstream_label in upstream.items():
            file_path = getattr(track, image_type.value)
            if file_path is not None and upstream_label is not None:
                path_to_source_label[str(file_path)] = upstream_label

    labels = file_list.data[path_col_id].apply(
        lambda p: path_to_source_label.get(str(p))
    )
    existing = file_list.data[source_label_col_id]
    has_existing_value = existing.apply(
        lambda value: bool(value) if isinstance(value, list) else pd.notna(value)
    )
    file_list.data[source_label_col_id] = existing.where(has_existing_value, labels)

    written = int(labels.notna().sum())
    logger.info(f"Wrote associated_source_image for {written} file(s).")


def _write_associated_specimen(
    file_list: FileList,
    tracks: list[SpecimenTrack],
) -> None:
    """
    Write the @id of the Specimen entity into the associated_subject column
    for the first image file belonging to a track.
    """
    path_col_id = get_path_column_id(file_list)
    if path_col_id is None:
        return

    specimen_col_id = get_or_add_associated_subject_column_id(file_list)

    path_to_specimen_id: dict[str, str] = {}

    for track in tracks:
        specimen_id = title_to_id(f"Specimen_{track.specimen_id}")

        if track.track_start == ImageType.FRAMES:
            for frame_path in track.frames:
                path_to_specimen_id[str(frame_path)] = specimen_id
        else:
            for upstream_type in [
                ImageType.TILT_SERIES, 
                ImageType.ALIGNED_TILT_SERIES, 
                ImageType.TOMOGRAM, 
                ImageType.DENOISED_TOMOGRAM,
            ]:
                if track.track_start == upstream_type:
                    file_path = getattr(track, upstream_type.value)
                    if file_path is not None:
                        path_to_specimen_id[str(file_path)] = specimen_id
                    if upstream_type == ImageType.TOMOGRAM:
                        denoised_tomo_path = getattr(track, ImageType.DENOISED_TOMOGRAM.value)
                        if denoised_tomo_path is not None:
                            path_to_specimen_id[str(denoised_tomo_path)] = specimen_id
                    break

    values = file_list.data[path_col_id].apply(
        lambda p: path_to_specimen_id.get(str(p))
    )
    file_list.data[specimen_col_id] = values

    written = int(values.notna().sum())
    logger.info(f"Wrote associated_subject for {written} file(s).")


def _write_associated_protocol(
    file_list: FileList,
    tracks: list[SpecimenTrack],
    dataset_configs: list[DatasetModificationConfig],
) -> None:
    """
    Write the @id(s) of Protocol entities into the associated_protocol column
    for image files whose image type is mapped to a protocol in the
    per-dataset specimen_tracks.protocol_titles config.

    Where multiple protocols are mapped to a single image type, the value
    is a serialised list e.g. "['#Protocol_a', '#Protocol_b']".
    """
    path_col_id = get_path_column_id(file_list)
    if path_col_id is None:
        return

    protocol_col_id = file_list.get_column_id_by_property(str(BIA.associatedProtocol))
    if protocol_col_id is None:
        logger.warning("No associated_protocol column found in file list; skipping.")
        return
    if file_list.data[protocol_col_id].dtype != object:
        file_list.data[protocol_col_id] = file_list.data[protocol_col_id].astype(object)

    # Build dataset_name -> protocol_titles lookup keyed by ImageType value
    dataset_protocol_map: dict[str, dict[str, list[str]]] = {}
    for dc in dataset_configs:
        if dc.specimen_tracks and dc.specimen_tracks.protocol_titles:
            dataset_protocol_map[dc.name] = dc.specimen_tracks.protocol_titles

    path_to_protocol: dict[str, str] = {}

    for track in tracks:
        for image_type in [
            ImageType.TILT_SERIES,
            ImageType.ALIGNED_TILT_SERIES,
            ImageType.TOMOGRAM,
            ImageType.DENOISED_TOMOGRAM,
        ]:
            file_path = getattr(track, image_type.value)
            if file_path is None:
                continue

            dataset_name = track.dataset_for.get(image_type.value)
            if dataset_name is None:
                continue

            protocol_titles_by_type = dataset_protocol_map.get(dataset_name, {})
            raw = protocol_titles_by_type.get(image_type.value)
            if raw is None:
                continue

            titles = [raw] if isinstance(raw, str) else raw
            ids = [title_to_id(t) for t in titles]
            value = str(ids) if len(ids) > 1 else ids[0]
            path_to_protocol[str(file_path)] = value

    values = file_list.data[path_col_id].apply(
        lambda p: path_to_protocol.get(str(p))
    )
    file_list.data[protocol_col_id] = values

    written = int(values.notna().sum())
    logger.info(f"Wrote associated_protocol for {written} file(s).")


def _write_specimen_metadata_to_file_list(
    file_list: FileList,
    tracks: list[SpecimenTrack],
    dataset_configs: list[DatasetModificationConfig],
) -> None:
    path_to_label = _generate_labels(tracks)
    _write_label_column(file_list, path_to_label)
    _write_source_image_labels(file_list, tracks, path_to_label)
    _write_associated_specimen(file_list, tracks)
    _write_associated_protocol(file_list, tracks, dataset_configs)


def assign_specimen_tracks(
    ro_crate_metadata: BIAROCrateMetadata,
    file_list: FileList,
    config: ModificationConfig,
) -> None:
    """
    Identify specimen tracks across all datasets and write Specimen entities 
    to the metadata graph, and labels, associated_source_image, associated_subject,
    and associated_protocol values to the file list.
    """
    # Datasets that contribute typed images to track identification, via either
    # images.by_type or typed entries in additional_files.images.
    def _has_typed_images(d: DatasetModificationConfig) -> bool:
        if d.images is not None and d.images.by_type:
            return True
        if d.additional_files is not None:
            return any(
                img.image_type is not None and img.image_type != IMAGE_ASSIGNMENT_TYPE_KEY
                for img in d.additional_files.images
            )
        return False

    dataset_configs_for_tracks = [d for d in config.datasets if _has_typed_images(d)]
    dataset_configs_with_additional_specimen_data = [
        d for d in config.datasets if d.specimen_tracks is not None
    ]

    track_df = _build_track_dataframe(
        file_list,
        ro_crate_metadata,
        dataset_configs_for_tracks,
        config.specimen_tracks
    )

    if track_df.empty:
        logger.warning("Specimen track identification: no files could be classified.")
        return

    tracks = _merge_tracks(track_df)
    logger.info(f"Identified {len(tracks)} specimen track(s).")

    specimen_metadata = _resolve_specimen_metadata(
        tracks, 
        config.specimen_defaults, 
        dataset_configs_with_additional_specimen_data
    )

    for spec_meta in specimen_metadata:
        specimen_entity = _make_specimen_entities(spec_meta)
        ro_crate_metadata.add_entity(specimen_entity)
        logger.debug(f"Added Specimen: {specimen_entity.id}")

    _write_specimen_metadata_to_file_list(
        file_list, 
        tracks, 
        dataset_configs_with_additional_specimen_data
    )

    for dataset_config in dataset_configs_with_additional_specimen_data:
        _apply_dataset_track_metadata(ro_crate_metadata, dataset_config, tracks)
