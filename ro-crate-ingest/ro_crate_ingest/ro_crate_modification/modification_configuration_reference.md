## Modification configuration reference

### Top-level keys

| Key | Required | Description |
|---|---|---|
| `study_metadata` | No | Optional additions to the Study entity. |
| `rembis` | No | Study-wide REMBI entities to add. |
| `specimen_defaults` | Required if `specimen_tracks` present | Default biosample/SIPP for all specimens. |
| `specimen_tracks` | No | Cross-dataset specimen ID extraction strategy. |
| `datasets` | No | Per-dataset modification instructions. |
| `pruning` | No | Placeholder; not yet implemented. |


### `rembis`

All sub-keys are optional lists. Entities are added in this order:
protocols → biosamples (+ taxons) → SIPPs → IAPs → annotation methods.

| Sub-key | Maps to |
|---|---|
| `protocols` | `ro_crate_models.Protocol` |
| `biosamples` | `ro_crate_models.BioSample` + `Taxon` |
| `specimen_imaging_preparation_protocols` | `ro_crate_models.SpecimenImagingPreparationProtocol` |
| `image_acquisition_protocols` | `ro_crate_models.ImageAcquisitionProtocol` |
| `annotation_methods` | `ro_crate_models.AnnotationMethod` |

Note: `BioSample.growthProtocol` is a single reference; only the first
`growth_protocol_title` is used if multiple are given.

Note: `Taxon` in the RO-Crate model has no `ncbi_id` field. The value is
accepted in the config for completeness but is not currently written to
the RO-Crate entity.


### `specimen_tracks` (top-level)

Exactly one identification strategy may be active:

| Strategy | When to use |
|---|---|
| `patterns` | Specimen ID appears directly in the file path via a regex. Each pattern must contain at least one capture group. Multiple patterns are tried in order; the first match wins. |
| `pattern_alias_mappings` | IDs appear in multiple zero-padded forms across datasets. Maps a canonical `\d{N}` regex to a list of alias patterns. |
| `literal_alias_mappings` | No algorithmic link between a specimen's files. Maps a canonical specimen ID to a list of glob aliases. |

When using `patterns`, all patterns are tried in order against each file
path. The capture group of the first matching pattern becomes the specimen
ID. This makes `patterns` suitable for datasets where different files use
different naming conventions — as long as each convention can be expressed
as a distinct regex.


### `datasets[].name`

Must match the `name`/`title` field of a Dataset entity already present
in the minimal RO-Crate exactly.

Dataset names must be unique within a config file.

After all named datasets have been processed, any remaining unassigned
files are automatically placed into a `"Default dataset"` entity. This
is unconditional — no YAML entry is needed or supported for it.


### `datasets[].images`

Two mutually exclusive forms:

**Flat (Scenario 1):** a glob pattern list under `images.patterns:`. All
matches receive `bia:Image` in the file list.

```yaml
images:
  patterns:
    - "**/*.tif"
```

**Keyed (Scenario 3):** a `by_type` dict. Valid keys are the `ImageType`
vocabulary (`frames`, `tilt_series`, `aligned_tilt_series`, `tomogram`,
`denoised_tomogram`) plus `image` for files that are images but do not
belong to a specimen track. All matches still receive `bia:Image` in the
file list; the key is used only during specimen track classification.

```yaml
images:
  by_type:
    tilt_series: "**/*.mrc.st"
    tomogram:
      - "**/*.rec.mrc"
      - "**/*.mrc"
    image: "**/*_overview.png"
```


### `datasets[].additional_files`

Assigns currently-unassigned files to this dataset, with optional image
marking. At least one of `data_directories` or `patterns` must be present.
Files already assigned to any dataset are never re-assigned.

```yaml
additional_files:
  data_directories:
    - "data/extra/"
  patterns:
    - "**/*.tif"
  images:
    - patterns: "**/*.tif"
      image_type: "tilt_series"
```

| Field | Required | Description |
|---|---|---|
| `data_directories` | One of these | Directory prefix(es) to narrow the candidate pool of unassigned files. |
| `patterns` | One of these | Glob pattern(s) applied within the candidate pool. |
| `images` | No | Image assignment entries for subsets of the assigned files. |

Each `images` entry:

| Field | Required | Description |
|---|---|---|
| `patterns` | Yes | Glob patterns identifying which assigned files are images. |
| `image_type` | No | `ImageType` value for track participation, or `image` for a plain image. Omit for plain images. |

`additional_files` runs before the `images` block within the same dataset
step, so newly-assigned files are visible to `images` pattern matching.

Typed `image_type` values (anything other than `image`) require the
top-level `specimen_tracks` block to be present (validation enforces this).


### `datasets[].image_groups`

Sub-dataset groups of track-less images used to assign protocol
associations at finer than dataset granularity. Each entry requires glob
patterns and a non-empty list of protocol titles.

```yaml
image_groups:
  - patterns: "**/*.tif"
    protocol_titles:
      - "Fluorescence imaging protocol"
  - patterns: "**/*.mrc"
    protocol_titles:
      - "EM acquisition protocol"
```

| Field | Required | Description |
|---|---|---|
| `patterns` | Yes | Glob patterns. Files must already be assigned as images (via `images` or `additional_files`). |
| `protocol_titles` | Yes | Protocol titles to write to `associated_protocol` in the file list. Must be non-empty. |

`image_groups` can be combined with `images`, `additional_files`,
`associations`, and `specimen_tracks` in the same dataset block.


### `datasets[].associations`

Explicit REMBI associations written to the Dataset entity. All fields are
optional; include only those relevant to this dataset.

```yaml
associations:
  image_acquisition_protocol_titles:
    - "Cryo-electron tomography"
  biosample_titles:
    - "Human HeLa cells"
  specimen_imaging_preparation_protocol_titles:
    - "Cryo-vitrification by plunge freezing"
  protocol_titles:
    - "HeLa cell culture protocol"
  annotation_method_titles:
    - "Manual segmentation"
  image_analysis_method_titles: []
  image_correlation_method_titles: []
```

`associations` can be combined with `images`, `additional_files`,
`image_groups`, and/or `specimen_tracks` in the same dataset block.


### `datasets[].specimen_tracks`

Only meaningful when the top-level `specimen_tracks` block is also present.
Provides per-dataset IAP/protocol title assignments and per-specimen
metadata overrides.

`image_acquisition_protocol_title` and `protocol_titles` are keyed by
either `dataset` (applies to the dataset as a whole) or an `ImageType`
value (applies only to images of that type). For simple flat associations
not needing image-type keying, prefer the `associations` block instead.

`specimen_groups` entries override `specimen_defaults` for specific
specimens, identified by explicit ID list (`specimen_ids`) or by regex
pattern (`specimen_id_pattern`). Each entry must override at least one
of `biosample_title` or `specimen_imaging_preparation_protocol_titles`.

A dataset block that has `images.by_type`, `specimen_groups`, or typed
`additional_files` images requires the top-level `specimen_tracks` block
to be present (validation enforces this). A dataset block that only
carries IAP/protocol titles in `specimen_tracks` without those features
does not.

A dataset block with no `specimen_tracks` block at all simply participates
in image assignment but contributes no track metadata — its images are
still included in track identification if they match the specimen ID
patterns.
