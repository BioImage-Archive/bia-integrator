import difflib
import logging
import pathlib
# import re
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq

from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.image_tracks import (
    ImageTrack,
    ImageType,
)

logger = logging.getLogger(__name__)


def infer_frame_pattern(frame_files: list[pathlib.Path]) -> str | None:
    """
    Given a list of frame file paths (all from one specimen), infer the
    file pattern by replacing the variable numeric/tilt-angle parts with {}.

    For example:
        raw_frames/b3g1_SR_ts50_101_0000_-15.0.tif
        raw_frames/b3g1_SR_ts50_101_0001_-15.0.tif
        ...
    becomes:
        raw_frames/b3g1_SR_ts50_101_{}_{}.tif

    Uses difflib.SequenceMatcher to identify varying regions across all files,
    then replaces each varying region with {}.
    """
    if not frame_files:
        return None

    str_paths = [str(p) for p in sorted(frame_files)]
    if len(str_paths) == 1:
        return str_paths[0]

    first = str_paths[0]

    # Collect all character positions in `first` that vary across other paths
    varying_positions: set[int] = set()
    matcher = difflib.SequenceMatcher()
    matcher.set_seq2(first)
    for other in str_paths[1:]:
        matcher.set_seq1(other)
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != "equal":
                # j1:j2 are the positions in `first` (seq2) that differ
                varying_positions.update(range(j1, j2))

    if not varying_positions:
        return first

    # Build the pattern from `first`, replacing varying regions with {}
    result_chars: list[str] = []
    in_replacement = False
    for i, ch in enumerate(first):
        if i in varying_positions:
            if not in_replacement:
                result_chars.append("{}")
                in_replacement = True
        else:
            in_replacement = False
            result_chars.append(ch)

    return "".join(result_chars)


def _protocol_title_value(titles: list[str]) -> str | list:
    """
    Return a single dq string if there is one title, or a list of dq strings
    if there are multiple. Matches the output convention for protocol_title.
    """
    if len(titles) == 1:
        return dq(titles[0])
    return [dq(t) for t in titles]


def _iap_config(dataset_config: dict) -> dict[str, list[str]]:
    """
    Parse the image_acquisition_protocol_title block from a dataset config.

    Returns a dict keyed by either 'dataset' or ImageType values, mapping to
    lists of protocol titles.
    """
    iap_tile = dataset_config.get("image_acquisition_protocol_title")
    if iap_tile is None:
        return {}
    return {k: ([v] if isinstance(v, str) else v) for k, v in iap_tile.items()}


def _protocol_titles_config(dataset_config: dict) -> dict[str, list[str]]:
    """
    Parse the protocol_titles block from a dataset config.

    Returns a dict keyed by ImageType values, mapping to lists of titles.
    """
    protocol_titles = dataset_config.get("protocol_titles", {})
    return {k: ([v] if isinstance(v, str) else v) for k, v in protocol_titles.items()}


def build_frames_assigned_images(
    tracks: list[ImageTrack],
    dataset_name: str,
    iap_titles: dict[str, list[str]],
    protocol_titles: dict[str, list[str]]
) -> list[dict]:
    """
    Build assigned_images entries for raw movie frame collections.

    Only includes tracks whose frames belong to dataset_name.
    iap is the parsed image_acquisition_protocol_title dict; image-type-level
    IAPs for 'frames' are attached per entry here (dataset-level IAPs are
    handled in build_dataset_blocks via assigned_dataset_rembis).
    """
    frames_iap_titles = iap_titles.get(ImageType.FRAMES, [])
    frames_protocol_titles = protocol_titles.get(ImageType.FRAMES, [])

    entries = []
    for track in tracks:
        if track.dataset_for.get(ImageType.FRAMES) != dataset_name:
            continue
        if not track.frames:
            continue
        pattern = infer_frame_pattern(track.frames)
        if pattern is None:
            logger.warning(
                f"Could not infer frame pattern for specimen {track.specimen_id}; skipping."
            )
            continue
        entry: dict = {
            "label_prefix": dq(f"Specimen_{track.specimen_id} frames"),
            "file_pattern": dq(pattern),
            "specimen_title": dq(f"Specimen_{track.specimen_id}"),
        }
        if frames_iap_titles:
            entry["image_acquisition_protocol_title"] = _protocol_title_value(
                frames_iap_titles
            )
        if frames_protocol_titles:
            entry["protocol_title"] = _protocol_title_value(frames_protocol_titles)
        entries.append(entry)
    return entries


def build_tilt_series_assigned_images(
    tracks: list[ImageTrack],
    dataset_name: str,
    iap_titles: dict[str, list[str]], 
    protocol_titles: dict[str, list[str]]
) -> list[dict]:
    """
    Build assigned_images entries for unaligned and aligned tilt series.

    Only includes tracks whose tilt_series / aligned_tilt_series belong to
    dataset_name. Cross-dataset input linkages (back to frames) are preserved
    regardless of which dataset those frames came from.
    """
    ts_protocol_titles = protocol_titles.get(ImageType.TILT_SERIES, [])
    ts_iap_titles = iap_titles.get(ImageType.TILT_SERIES, [])

    ats_protocol_titles = protocol_titles.get(ImageType.ALIGNED_TILT_SERIES, [])
    ats_iap_titles = iap_titles.get(ImageType.ALIGNED_TILT_SERIES, [])

    entries = []
    for track in tracks:
        # Unaligned tilt series
        if (
            track.tilt_series is not None
            and track.dataset_for.get(ImageType.TILT_SERIES) == dataset_name
        ):
            entry: dict = {
                "label": dq(f"Specimen_{track.specimen_id} tilt_series"),
                "file_pattern": dq(str(track.tilt_series)),
            }
            if track.frames:
                frame_pattern = infer_frame_pattern(track.frames)
                if frame_pattern:
                    entry["input_label_prefix"] = dq(f"Specimen_{track.specimen_id} frames")
                    entry["input_file_pattern"] = dq(frame_pattern)
            else:
                if track.track_start:
                    entry["specimen_title"] = dq(f"Specimen_{track.specimen_id}")
                else:
                    raise ValueError(
                        f"Track for specimen {track.specimen_id} has no frames, but the tilt series "
                        "is not marked as track_start — specimen must be assigned as early in track as possible."
                        )
            if ts_protocol_titles:
                entry["protocol_title"] = _protocol_title_value(ts_protocol_titles)
            if ts_iap_titles:
                entry["image_acquisition_protocol_title"] = _protocol_title_value(
                    ts_iap_titles
                )
            entries.append(entry)

        # Aligned tilt series
        if (
            track.aligned_tilt_series is not None
            and track.dataset_for.get(ImageType.ALIGNED_TILT_SERIES) == dataset_name
        ):
            entry = {
                "label": dq(f"Specimen_{track.specimen_id} aligned_tilt_series"),
                "file_pattern": dq(str(track.aligned_tilt_series)),
            }
            if track.tilt_series is not None:
                entry["input_label"] = dq(
                    f"Specimen_{track.specimen_id} tilt_series"
                )
            elif track.frames is not None:
                frame_pattern = infer_frame_pattern(track.frames)
                if frame_pattern:
                    entry["input_label_prefix"] = dq(f"Specimen_{track.specimen_id} frames")
                    entry["input_file_pattern"] = dq(frame_pattern)
            else:
                if track.track_start:
                    entry["specimen_title"] = dq(f"Specimen_{track.specimen_id}")
                else:
                    raise ValueError(
                        f"Track for specimen {track.specimen_id} has no frames or tilt series, but the aligned tilt series "
                        "is not marked as track_start — specimen must be assigned as early in track as possible."
                        )
            if ats_protocol_titles:
                entry["protocol_title"] = _protocol_title_value(ats_protocol_titles)
            if ats_iap_titles:
                entry["image_acquisition_protocol_title"] = _protocol_title_value(
                    ats_iap_titles
                )
            entries.append(entry)

    return entries


def build_tomogram_assigned_images(
    tracks: list[ImageTrack],
    dataset_name: str,
    iap_titles: dict[str, list[str]], 
    protocol_titles: dict[str, list[str]],
) -> list[dict]:
    """
    Build assigned_images entries for reconstructed tomograms.

    Only includes tracks whose tomogram belongs to dataset_name.
    """
    tomo_protocol_titles = protocol_titles.get(ImageType.TOMOGRAMS, [])
    tomo_iap_titles = iap_titles.get(ImageType.TOMOGRAMS, [])

    entries = []
    for track in tracks:
        if (
            track.tomogram is None
            or track.dataset_for.get(ImageType.TOMOGRAMS) != dataset_name
        ):
            continue
        entry: dict = {
            "label": dq(f"Specimen_{track.specimen_id} tomogram"),
            "file_pattern": dq(str(track.tomogram)),
        }
        if track.aligned_tilt_series is not None:
            entry["input_label"] = dq(
                f"Specimen_{track.specimen_id} aligned_tilt_series"
            )
        elif track.tilt_series is not None:
            entry["input_label"] = dq(
                f"Specimen_{track.specimen_id} tilt_series"
            )
        elif track.frames is not None:
            frame_pattern = infer_frame_pattern(track.frames)
            if frame_pattern:
                entry["input_label_prefix"] = dq(f"Specimen_{track.specimen_id} frames")
                entry["input_file_pattern"] = dq(frame_pattern)
        else:
            if track.track_start:
                entry["specimen_title"] = dq(f"Specimen_{track.specimen_id}")
            else:
                raise ValueError(
                    f"Track for specimen {track.specimen_id} has no frames or tilt series (aligned or otherwise), but the tomogram "
                    "is not marked as track_start — specimen must be assigned as early in track as possible."
                    )
        if tomo_protocol_titles:
            entry["protocol_title"] = _protocol_title_value(tomo_protocol_titles)
        if tomo_iap_titles:
            entry["image_acquisition_protocol_title"] = _protocol_title_value(
                tomo_iap_titles
            )
        entries.append(entry)
    return entries


def build_dataset_blocks(
    tracks: list[ImageTrack],
    dataset_config: dict,
) -> dict:
    """
    Build a single dataset output block for one dataset config entry.
    All image types (frames, tilt series, tomograms) are combined into
    a single assigned_images list.

    image_acquisition_protocol_title supports two modes:
        dataset-level : {'dataset': ['Title']}  — attached to the dataset block
                        via assigned_dataset_rembis (the common case).
        type-level    : {'frames': ['Title']}   — attached per assigned_image
                        entry for that image type only.

    protocol_titles is keyed by image type and attached per assigned_image entry.
    Multiple titles produce a list; a single title produces a plain string.
    """
    dataset_name = dataset_config.get("name")
    if dataset_name is None:
        raise ValueError(f"Dataset config {dataset_config} has no 'name' key.")

    iap_titles = _iap_config(dataset_config)
    protocol_titles = _protocol_titles_config(dataset_config)

    assigned_images = [
        *build_frames_assigned_images(tracks, dataset_name, iap_titles, protocol_titles),
        *build_tilt_series_assigned_images(tracks, dataset_name, iap_titles, protocol_titles),
        *build_tomogram_assigned_images(tracks, dataset_name, iap_titles, protocol_titles),
    ]

    block: dict = {
        "title": dq(dataset_name),
        "assigned_images": assigned_images,
    }

    dataset_iap_titles = iap_titles.get("dataset", [])
    if dataset_iap_titles:
        block["assigned_dataset_rembis"] = [
            {
                "image_acquisition_protocol_title": _protocol_title_value(
                    dataset_iap_titles
                )
            }
        ]

    return block


def assign_specimen_metadata(
    tracks: list[ImageTrack],
    global_defaults: dict,
    datasets_config: list[dict] | None = None,
) -> list[dict]:
    """
    Build Specimen dicts from tracks using a cascade of metadata sources:

        global defaults  <  specimen_groups (from any dataset)

    specimen_groups entries across all dataset blocks are merged into a single
    lookup; later dataset blocks take precedence for the same specimen_id.

    Each specimen_groups entry is a dict with:
        specimen_ids                                 : list[str]
        biosample_title                              : str  (optional)
        specimen_imaging_preparation_protocol_titles : list[str]  (optional)
    """
    # there are only groups if there are overrides for specimens in dataset blocks
    group_lookup: dict[str, dict] = {}
    for dataset_config in (datasets_config or []):
        for group in dataset_config.get("specimen_groups", []):
            group_meta = {k: v for k, v in group.items() if k != "specimen_ids"}
            for sid in group.get("specimen_ids", []):
                group_lookup[str(sid)] = group_meta

    specimens: list[dict] = []
    for track in tracks:
        sid = track.specimen_id

        biosample_title = global_defaults.get("biosample_title")
        # NOTE: create a new list to avoid YAML alias references — 
        # the belt to the yaml writer's 'ignore alias' braces
        prep_protocol_titles = list(
            global_defaults.get("specimen_imaging_preparation_protocol_titles", [])
        )

        # TODO: match patterns for specimen id here
        if sid in group_lookup:
            override = group_lookup[sid]
            if "biosample_title" in override:
                biosample_title = override["biosample_title"]
            if "specimen_imaging_preparation_protocol_titles" in override:
                prep_protocol_titles = list(
                    override["specimen_imaging_preparation_protocol_titles"]
                )

        specimens.append(
            {
                "title": f"Specimen_{sid}",
                "biosample_title": biosample_title,
                "specimen_imaging_preparation_protocol_title": prep_protocol_titles,
            }
        )

    return specimens
