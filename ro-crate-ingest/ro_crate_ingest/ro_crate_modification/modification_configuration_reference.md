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


### Enrichment order

Configuration is applied in this order:

1. `study_metadata`
2. top-level `rembis`
3. each named dataset, in config order:
   a. `associations`
   b. `additional_files`
   c. `images`
   d. `image_groups`
   e. `annotations`
4. top-level `specimen_tracks`, if configured
5. default-dataset assignment for any remaining unassigned files

The order matters. For example, `additional_files` runs before `images`, so
newly assigned files can be marked as images in the same dataset block, and
`image_groups` runs after image assignment so it can match image rows.
If two pattern-based steps match the same file and write the same file-list
column, the later step overwrites the earlier value and logs a warning.


### `study_metadata`

Optional additions to the Study entity at `./`.

```yaml
study_metadata:
  description: "Updated study description."
  see_also:
    - "https://example.org/related-resource"
  related_publication:
    - "https://doi.org/10.1234/example"
```

| Field | Required | Description |
|---|---|---|
| `description` | No | Replaces the existing Study description when provided. |
| `see_also` | No | Appended to existing `seeAlso` values. |
| `related_publication` | No | DOI/identifier values used to create Publication entities and merge `relatedPublication` references. |


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

Note: when `ncbi_id` is provided for a taxon, it is used as the `Taxon`
entity `@id`. If it is omitted, the fallback is a title-derived ID from
`scientific_name`.


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

When top-level `specimen_tracks` is present, `specimen_defaults` is required
and must include both a `biosample_title` and at least one
`specimen_imaging_preparation_protocol_titles` value.


### `specimen_defaults`

Default metadata for every Specimen generated during specimen-track
assignment.

```yaml
specimen_defaults:
  biosample_title: "Yeast cells"
  specimen_imaging_preparation_protocol_titles:
    - "Cryo-vitrification"
```

| Field | Required | Description |
|---|---|---|
| `biosample_title` | Yes, when top-level `specimen_tracks` is present | BioSample title to reference from each generated Specimen unless a matching `specimen_group` overrides it. |
| `specimen_imaging_preparation_protocol_titles` | Yes, when top-level `specimen_tracks` is present | One or more SIPP titles to reference from each generated Specimen unless a matching `specimen_group` overrides them. |


### `datasets[].name`

Must match the `name`/`title` field of a Dataset entity already present
in the minimal RO-Crate exactly.

Dataset names must be unique within a config file.

After all named datasets have been processed, any remaining unassigned
files are automatically placed into a `"Default dataset"` entity. The
default-dataset step always runs, but the entity is only created if
unassigned files remain. When created, it is also added to the Study
entity's `hasPart` list. No YAML entry is needed or supported for it.


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
`denoised_tomogram`, `segmentation`) plus `image` for files that are images
but do not belong to a specimen track. All matches still receive `bia:Image`
in the file list; the key is used only during specimen track classification.

```yaml
images:
  by_type:
    tilt_series: "**/*.mrc.st"
    tomogram:
      - "**/*.rec.mrc"
      - "**/*.mrc"
    segmentation: "**/*.mrcseg"
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


### `datasets[].annotations`

Assign annotation files within a dataset. Each entry matches files by glob
pattern and writes annotation metadata into the file list:

- file `type` is set to `bia:AnnotationData`
- `label`/name is set from the matched file stem, unless the pattern is a
  single literal path, in which case that path stem is used
- `associated_annotation_method` is written from `annotation_method_titles`
- `associated_source_image` is written from `associated_source_image`; values
  should be labels of image rows that exist after enrichment

The Dataset entity is also updated with the unique AnnotationMethod
references named by the annotation entries.

```yaml
annotations:
  - patterns:
      - "**/*_particles.star"
    annotation_method_titles:
      - "Particle picking"
    associated_source_image:
      - "Specimen_001 tomogram"
  - patterns:
      - "**/*_mito_labels.csv"
    annotation_method_titles:
      - "Particle picking"
    associated_source_image:
      - "Specimen_002 tomogram"
      - "Specimen_003 tomogram"
```

| Field | Required | Description |
|---|---|---|
| `patterns` | Yes | Glob patterns identifying annotation files in the dataset. |
| `annotation_method_titles` | Yes | AnnotationMethod titles to write to `associated_annotation_method`. Must be non-empty. |
| `associated_source_image` | Yes | Source image label(s) to write to `associated_source_image`. Must be non-empty, and should match image labels present after enrichment. |

For specimen-track cryoET data, generated image labels use the specimen ID and
image type, such as `Specimen_001 tomogram` or `Specimen_001 denoised_tomogram`.
Use those generated labels when an annotation file refers to a track image. The
modifier writes the configured values as file-list metadata; downstream
RO-Crate parsing validates whether the references resolve sensibly.

`annotations` can be combined with `images`, `additional_files`,
`image_groups`, `associations`, and/or `specimen_tracks` in the same dataset block.
Because annotation assignment runs after `images`, an annotation pattern that
also matches image rows will overwrite their `type` value and log a warning.

If the file list does not already have a label/name column, annotation
assignment adds one before writing annotation labels. If the dataset or file
path column is absent, annotation assignment is skipped for that dataset.


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

Processed during the top-level `specimen_tracks` enrichment step. Provides
per-dataset IAP/protocol/annotation-method title assignments and per-specimen
metadata overrides.

`image_acquisition_protocol_title`, `protocol_titles`, and
`annotation_method_titles` are keyed by either `dataset` (applies to the
dataset as a whole) or an `ImageType` value (applies only to images of that
type). `annotation_method_titles` is useful for segmentation images, which
remain `bia:Image` rows but can carry an annotation-method association. For
simple flat associations not needing image-type keying, prefer the
`associations` block instead.

`source_image_types` is valid only for the `segmentation` target key. Its value
names the preferred upstream `ImageType` to write to `associated_source_image`
for segmentation rows. When omitted, segmentations prefer `tomogram`; if that
source is absent, the modifier falls back first to `denoised_tomogram`, then to
available upstream image labels in the order `aligned_tilt_series`,
`tilt_series`, `frames`.

```yaml
specimen_tracks:
  annotation_method_titles:
    segmentation:
      - "Manual segmentation"
  source_image_types:
    segmentation: "denoised_tomogram"
```

`specimen_groups` entries override `specimen_defaults` for specific
specimens, identified by explicit ID list (`specimen_ids`) or by regex
pattern (`specimen_id_pattern`). Each entry must override at least one
of `biosample_title` or `specimen_imaging_preparation_protocol_titles`.

A dataset block that has `images.by_type`, `specimen_groups`, or typed
`additional_files` images requires the top-level `specimen_tracks` block
to be present (validation enforces this). A dataset block that only carries
IAP/protocol/annotation-method titles in `specimen_tracks` without those
features may pass validation, but those titles are only applied when the
top-level `specimen_tracks` step runs. For simple dataset-level associations,
use `associations` instead.

A dataset block with no `specimen_tracks` block at all simply participates
in image assignment but contributes no track metadata — its images are
still included in track identification if they match the specimen ID
patterns.
