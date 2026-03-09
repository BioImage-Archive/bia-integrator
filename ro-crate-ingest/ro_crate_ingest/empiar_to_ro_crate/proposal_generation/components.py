import logging
import pathlib
import re
from ruamel.yaml.scalarstring import DoubleQuotedScalarString as dq

from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.image_tracks import (
    ImageTrack,
)
from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.image_types import (
    ImageType, 
    ImageTypeSpec, 
    IMAGE_TYPE_SPECS, 
)
from ro_crate_ingest.empiar_to_ro_crate.proposal_generation.proposal_config import (
    DatasetConfig,
    SpecimenDefaults,
    SpecimenGroup,
)

logger = logging.getLogger(__name__)


def infer_frame_pattern(
    frame_files: list[pathlib.Path],
    pattern_inference_delimiters: list[str]
) -> str | None:
    """
    Given a list of frame file paths (all from one specimen), infer the
    file pattern by replacing the variable parts with {}.

    Splits each path into tokens on the given delimiters, then compares
    token-by-token across all files. Tokens that are constant across all
    files are kept literal; tokens that vary become {}.

    For example:
        raw_frames/b3g1_SR_ts50_101_0000_-15.0.tif
        raw_frames/b3g1_SR_ts50_101_0001_-15.0.tif
        ...
    becomes:
        raw_frames/b3g1_SR_ts50_101_{}_-15.0.tif
    """
    if not frame_files:
        return None

    str_paths = [str(p) for p in sorted(frame_files)]
    if len(str_paths) == 1:
        return str_paths[0]

    escaped = [re.escape(d) for d in pattern_inference_delimiters]
    split_pattern = '(' + '|'.join(escaped) + ')'

    def split_with_delimiters(s: str) -> list[str]:
        return re.split(split_pattern, s)

    tokenised = [split_with_delimiters(p) for p in str_paths]

    lengths = {len(t) for t in tokenised}
    if len(lengths) > 1:
        logger.warning(
            "Frame files for a specimen have inconsistent token counts after splitting "
            f"on {pattern_inference_delimiters}; falling back to first path as pattern."
        )
        return str_paths[0]

    first_tokens = tokenised[0]
    result_parts = []
    for i, token in enumerate(first_tokens):
        if token in pattern_inference_delimiters:
            result_parts.append(token)
            continue
        if all(t[i] == token for t in tokenised[1:]):
            result_parts.append(token)
        else:
            result_parts.append('{}')

    return ''.join(result_parts)


def _protocol_title_value(titles: list[str]) -> str | list:
    """
    Return a single dq string if there is one title, or a list of dq strings
    if there are multiple. Matches the output convention for protocol_title.
    """
    if len(titles) == 1:
        return dq(titles[0])
    return [dq(t) for t in titles]


def _parse_protocol_title_config(raw: dict[str, str | list[str]] | None) -> dict[str, list[str]]:
    """
    Parse the image_acquisition_protocol_title or protocol_titles blocks from a DatasetConfig.

    Returns a dict keyed by either 'dataset' (only for IAP) or ImageType values, mapping to
    lists of protocol titles.
    """
    if raw is None:
        return {}
    return {k: ([v] if isinstance(v, str) else list(v)) for k, v in raw.items()}


def _get_track_file(track: ImageTrack, image_type: ImageType) -> pathlib.Path | None:
    """Return the file on a track for a given ImageType, or None."""
    return getattr(track, image_type.value, None)


def _build_single_file_assigned_image(
    track: ImageTrack,
    spec: ImageTypeSpec,
    iap_titles: list[str],
    pt_titles: list[str],
    pattern_inference_delimiters: list[str]
) -> dict:
    """
    Build one assigned_images entry for a single-file ImageType (i.e. anything
    except frames). Input linkage is resolved by walking spec.upstream_types in
    order, then falling back to frames (via label_prefix), then to track_start
    (specimen_title) if the track has no earlier images at all.
    """
    sid = track.specimen_id
    file_path = _get_track_file(track, spec.image_type)

    entry: dict = {
        "label": dq(f"Specimen_{sid} {spec.image_type.value}"),
        "file_pattern": dq(str(file_path)),
    }

    for upstream in spec.upstream_types:
        if _get_track_file(track, upstream) is not None:
            entry["input_label"] = dq(f"Specimen_{sid} {upstream.value}")
            break
    else:
        if track.frames:
            frame_pattern = infer_frame_pattern(track.frames, pattern_inference_delimiters)
            if frame_pattern:
                entry["input_label_prefix"] = dq(f"Specimen_{sid} frames")
                entry["input_file_pattern"] = dq(frame_pattern)
        else:
            if track.track_start == spec.image_type:
                entry["specimen_title"] = dq(f"Specimen_{sid}")
            else:
                raise ValueError(
                    f"Track for specimen {sid} has no upstream images for "
                    f"{spec.image_type.value}, but it is not marked as track_start. "
                    "Specimen must be assigned as early in the track as possible."
                )

    if pt_titles:
        entry["protocol_title"] = _protocol_title_value(pt_titles)
    if iap_titles:
        entry["image_acquisition_protocol_title"] = _protocol_title_value(iap_titles)

    return entry


def _build_assigned_images_for_type(
    tracks: list[ImageTrack],
    dataset_name: str,
    spec: ImageTypeSpec,
    iap_titles: dict[str, list[str]],
    protocol_titles: dict[str, list[str]],
    pattern_inference_delimiters: list[str]
) -> list[dict]:
    """
    General builder for a single non-frames ImageType.
    """
    type_iap_titles = iap_titles.get(spec.image_type, [])
    type_protocol_titles = protocol_titles.get(spec.image_type, [])

    entries = []
    for track in tracks:
        if _get_track_file(track, spec.image_type) is None:
            continue
        if track.dataset_for.get(spec.image_type) != dataset_name:
            continue
        entries.append(
            _build_single_file_assigned_image(
                track, spec, type_iap_titles, type_protocol_titles,
                pattern_inference_delimiters,
            )
        )
    return entries


def build_frames_assigned_images(
    tracks: list[ImageTrack],
    dataset_name: str,
    iap_titles: dict[str, list[str]],
    protocol_titles: dict[str, list[str]],
    pattern_inference_delimiters: list[str]
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
        pattern = infer_frame_pattern(track.frames, pattern_inference_delimiters)
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


def build_dataset_blocks(
    tracks: list[ImageTrack],
    dataset_config: DatasetConfig,
    pattern_inference_delimiters: list[str]
) -> dict:
    """
    Build a single dataset output block for one DatasetConfig entry.
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
    dataset_name = dataset_config.name

    iap_titles = _parse_protocol_title_config(dataset_config.image_acquisition_protocol_title)
    protocol_titles = _parse_protocol_title_config(dataset_config.protocol_titles)

    assigned_images = [
        *build_frames_assigned_images(
            tracks, dataset_name, iap_titles, protocol_titles,
            pattern_inference_delimiters,
        ),
        *(
            entry
            for spec in IMAGE_TYPE_SPECS
            for entry in _build_assigned_images_for_type(
                tracks, dataset_name, spec, iap_titles, protocol_titles,
                pattern_inference_delimiters,
            )
        ),
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
    specimen_defaults: SpecimenDefaults | None,
    dataset_configs: list[DatasetConfig] | None = None,
) -> list[dict]:
    """
    Build Specimen dicts from tracks using a cascade of metadata sources:

        specimen_defaults  <  specimen_groups (from any dataset)

    specimen_groups entries across all dataset blocks are merged into a single
    lookup; later dataset blocks take precedence for the same specimen_id, 
    but it is not anticipated that one specimen_id would appear twice.
    """
    group_lookup: dict[str, SpecimenGroup] = {}
    group_patterns: list[tuple[str, SpecimenGroup]] = []

    for dataset_config in (dataset_configs or []):
        for group in dataset_config.specimen_groups:
            if group.specimen_id_pattern is not None:
                group_patterns.append((group.specimen_id_pattern, group))
            else:
                for sid in group.specimen_ids:
                    group_lookup[sid] = group

    specimens: list[dict] = []
    for track in tracks:
        sid = track.specimen_id

        biosample_title = specimen_defaults.biosample_title if specimen_defaults else None
        prep_protocol_titles = (
            list(specimen_defaults.specimen_imaging_preparation_protocol_titles)
            if specimen_defaults else []
        )

        # Resolve override: exact match takes precedence over pattern match.
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
                prep_protocol_titles = list(
                    override.specimen_imaging_preparation_protocol_titles
                )

        specimens.append(
            {
                "title": f"Specimen_{sid}",
                "biosample_title": biosample_title,
                "specimen_imaging_preparation_protocol_title": prep_protocol_titles,
            }
        )

    return specimens
