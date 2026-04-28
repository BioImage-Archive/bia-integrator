# RO-Crate Modification Pipeline

## Overview

The modification pipeline takes a **minimal RO-Crate** — a lightweight
intermediate format containing only a Study entry and a file list — and
enriches it with study and REMBI metadata, image assignment, annotation
assignment, and specimen track information, producing a fully-described RO-Crate
suitable for ingest.

The pipeline aims to be source-agnostic, but currently is geared toward, 
and has been tested on, EMPIAR entries. 

```
minimal RO-Crate  +  modification_config.yaml
        │
        ▼
   apply_modifications()   [modifier.py]
        │
        ├── apply_enrichment()   [enricher.py]
        │       │
        │       ├── 1. Add study metadata                        [study.py]
        │       ├── 2. Add REMBI entities to metadata graph      [rembis.py]
        │       ├── 3. For each named dataset:
        │       │       a. Apply dataset-level REMBI associations [rembis.py]
        │       │       b. Assign additional unassigned files     [assignments.py]
        │       │       c. Assign images within the dataset       [assignments.py]
        │       │       d. Write image-group protocol refs        [assignments.py]
        │       │       e. Assign annotations within the dataset  [assignments.py]
        │       ├── 4. Identify specimen tracks + assign         [specimens.py]
        │       └── 5. Create default dataset for unassigned     [assignments.py]
        │
        └── apply_pruning()   [pruner.py — future]
```

Output is written to a `modified/` subdirectory alongside the input
RO-Crate. 

---

## CLI usage

```
# Apply a modification config to a minimal RO-Crate:
ro-crate-ingest modify-roc <path/to/minimal/ro-crate> <path/to/modification_config.yaml>

# Output is written to:
<path/to/minimal/ro-crate>/modified/ro-crate-metadata.json
<path/to/minimal/ro-crate>/modified/<file_list_name>.tsv
```

---

## Further documentation
Notes on modification scenarios and making an appropriate configuration are below; there is more detail available in [modification_configuration_reference](modification_configuration_reference.md) and [worked_examples](worked_examples.md).

---

## Enrichment order

The current enrichment step is intentionally ordered so later operations can
see the results of earlier ones:

1. Add configured information to the Study entity.
2. Add study-wide REMBI entities to the metadata graph.
3. For each named dataset:
   a. Apply explicit REMBI associations to the Dataset entity.
   b. Assign `additional_files` that are still unassigned to that dataset,
      optionally marking them as images.
   c. Apply `images` assignment to files already in the dataset, including
      files just added by `additional_files`.
   d. Apply `image_groups` protocol associations to image rows.
   e. Apply `annotations` assignment to annotation rows.
4. If top-level `specimen_tracks` is configured, identify tracks, create
   Specimen entities, and write track metadata to the file list.
5. Run the default-dataset step. If any file rows are still unassigned, a
   `"Default dataset"` entity is created if needed and those rows are assigned
   to it. No YAML entry is needed for the default dataset.

---

## Scenarios

*The scenarios below are numbered for reference only, and do not imply ordering
or exclusivity.*

### 1a. Image assignment

Files matching the given glob patterns are marked as `bia:Image` in the
file list. No specimen entities are created, no metadata graph changes are
made.

**Example config:**

```yaml
datasets:
  - name: "Fluorescence images of HeLa cells"
    images:
      patterns:
        - "**/*.tif"
        - "**/*.ome.tiff"

  - name: "Electron microscopy overview"
    images:
      patterns:
        - "**/*.mrc"
```

**What happens:**

1. For each named dataset, the enricher looks up the Dataset entity in the
   RO-Crate by its `name` field.
2. It filters the file list to rows where `_part_of_dataset` matches that
   entity's `@id`.
3. Each file whose path matches one of the glob patterns has its `type`
   column set to `bia:Image`.
4. After all named datasets are processed, any files that remain unassigned
   (no dataset membership) are automatically collected into a new Dataset
   entity titled `"Default dataset"`. The default-dataset step always runs,
   but the entity is only created when unassigned files remain. No config entry
   is needed.


### 1b. Assigning additional files to an existing dataset

When some files in the minimal RO-Crate have no dataset membership but
belong logically to an existing named dataset, the `additional_files` block
can pull them in. This is useful when the minimal step couldn't assign
them, or when files from a subdirectory should be grouped with an existing
imageset.

`additional_files` runs **before** the `images` block within the same
dataset step, so newly-assigned files are visible to pattern matching.

```yaml
datasets:
  - name: "Raw tilt series"
    additional_files:
      data_directories:
        - "data/extra_frames/"
      patterns:
        - "**/*.tif"
      images:
        - patterns: "**/*.tif"
          # image_type can be specified here (see below)
    images:
      by_type:
        tilt_series: "**/*.mrc.st"
```

**`additional_files` fields:**

| Field | Required | Description |
|---|---|---|
| `data_directories` | One of these | Directory prefixes; only unassigned files under these paths are considered. |
| `patterns` | One of these | Glob patterns applied within the candidate pool. |
| `images` | No | List of `AdditionalFileImageAssignment` entries marking subsets as images. |

At least one of `data_directories` or `patterns` must be present. Only
files that are currently unassigned (no dataset membership) are ever
affected.

Each `images` entry has:

| Field | Required | Description |
|---|---|---|
| `patterns` | Yes | Glob patterns identifying which additionally-assigned files are images. |
| `image_type` | No | An `ImageType` value (`frames`, `tilt_series`, etc.) for specimen track participation, or `image` for a plain non-track image. When absent, the file is a plain image. |


### 1c. Protocol assignment within a dataset (image_groups)

When a single dataset contains multiple distinct types of track-less images
that should receive different protocol associations, `image_groups` assigns
protocols at sub-dataset granularity. Each entry matches a subset of
image-assigned files in the dataset and writes protocol IDs to the
`associated_protocol` column.

```yaml
datasets:
  - name: "Correlative dataset"
    images:
      patterns:
        - "**/*.tif"
        - "**/*.mrc"
    image_groups:
      - patterns: "**/*.tif"
        protocol_titles:
          - "Fluorescence imaging protocol"
      - patterns: "**/*.mrc"
        protocol_titles:
          - "EM acquisition protocol"
```

Each `image_groups` entry has:

| Field | Required | Description |
|---|---|---|
| `patterns` | Yes | Glob patterns identifying matched image files within this dataset. Files must already be assigned as images. |
| `protocol_titles` | Yes | One or more Protocol titles to associate with matched files. Must be non-empty. |

`image_groups` can be combined with `images`, `additional_files`,
`associations`, and `specimen_tracks` in the same dataset block.


### 1d. Annotation assignment

Annotation assignment marks matched files in an existing dataset as
`bia:AnnotationData`, adds an annotation label, links the files to one or more
AnnotationMethod entities, and records the source image label(s) consumed by
downstream ingest.

```yaml
rembis:
  annotation_methods:
    - title: "Manual segmentation"
      protocol_description: "Segmentations drawn by expert annotators."
      method_type:
        - "manual annotation"

datasets:
  - name: "Tomogram annotations"
    annotations:
      - patterns:
          - "**/*_mask.json"
        annotation_method_titles:
          - "Manual segmentation"
        associated_source_image:
          - "Specimen_0001 tomogram"
```

Each `annotations` entry has:

| Field | Required | Description |
|---|---|---|
| `patterns` | Yes | Glob patterns identifying annotation files within the dataset. |
| `annotation_method_titles` | Yes | One or more AnnotationMethod titles. Values are resolved to `@id`s and written to `associated_annotation_method`; the Dataset also receives those AnnotationMethod associations. |
| `associated_source_image` | Yes | One or more source image labels written to `associated_source_image`. |

Annotation assignment runs after `additional_files`, `images`, and
`image_groups` for the same dataset. It expects the file list to already have
a label/name column; if that column is absent, annotation assignment is skipped
for that dataset.


### 2. REMBI assignment and study metadata

Used to add REMBI and study metadata to the RO-Crate graph. The `datasets` 
block is optional; include it only to attach IAP or protocol references 
to specific Dataset entities via `associations`.

```yaml
study_metadata:
  description: "Optional free-text description to add to the Study entity."
  see_also:
    - "https://example.org/related-resource"
  related_publication:
    - "https://doi.org/10.1234/example"

rembis:
  biosamples:
    - title: "Human HeLa cells"
      biological_entity_description: "HeLa cervical cancer cell line"
      organism_classification:
        - common_name: "human"
          scientific_name: "Homo sapiens"
          ncbi_id: "NCBI:txid9606"
      growth_protocol_title: "HeLa cell culture protocol"

  protocols:
    - title: "HeLa cell culture protocol"
      protocol_description: "..."

  image_acquisition_protocols:
    - title: "Cryo-electron tomography"
      protocol_description: "..."
      imaging_instrument_description: "Titan Krios G3i"
      fbbi_id: ["obo:FBbi_00000256"]
      imaging_method_name: ["Cryo-electron tomography"]

datasets:
  - name: "Unaligned multi-frame micrographs"
    associations:
      image_acquisition_protocol_titles:
        - "Cryo-electron tomography"
      biosample_titles:
        - "Human HeLa cells"
```

**What happens:**

1. Study metadata is added (*NOTE:* `description` is not strictly additive;
   it overwrites any existing description).
2. Protocol entities are added to the graph.
3. Taxon and BioSample entities are added.
4. SIPP, IAP, and AnnotationMethod entities are added.
5. If `datasets` blocks are present, their `associations` are written to
   the corresponding Dataset entities.
6. No image, annotation, or specimen-track file-list changes are made by this
   scenario. The final default-dataset step still runs and may assign any
   remaining unassigned files.


### 3. REMBI + specimen track assignment (including images)

Specimen track assignment is effectively an extension of image assignment, 
linking types of images. Files are assigned as images and then grouped
into per-specimen tracks spanning multiple datasets. Specimen entities 
are created in the metadata graph, and the `associated_source_image` column is
populated in the file list to express the upstream relationship between 
images in a track. Though a full set of REMBI metadata may not be required
here, specimen tracks beget specimens, which should have a BioSample (which
then might have a `growth_protocol`) and a SIPP. 

The generated Specimen entities reference BioSamples and SIPPs by title-derived
IDs from `specimen_defaults` and any matching `specimen_groups`.

```yaml
rembis:
  protocols:
    - title: "Yeast culture protocol"
      protocol_description: "Standard YPD growth at 30°C."
    - title: "Tomogram reconstruction"
      protocol_description: "IMOD-based reconstruction."

  biosamples:
    - title: "Yeast cells"
      biological_entity_description: "S. cerevisiae BY4741"
      organism_classification:
        - common_name: "baker's yeast"
          scientific_name: "Saccharomyces cerevisiae"
          ncbi_id: "NCBI:txid4932"
      growth_protocol_title: "Yeast culture protocol"

  specimen_imaging_preparation_protocols:
    - title: "Cryo-vitrification"
      protocol_description: "Plunge-frozen in liquid ethane."

  image_acquisition_protocols:
    - title: "Cryo-ET"
      protocol_description: "..."
      imaging_instrument_description: "Titan Krios"
      fbbi_id: ["obo:FBbi_00000256"]
      imaging_method_name: ["Cryo-electron tomography"]

  annotation_methods:
    - title: "Manual segmentation"
      protocol_description: "Manual segmentation of tomogram structures."
      method_type:
        - "segmentation"

specimen_defaults:
  biosample_title: "Yeast cells"
  specimen_imaging_preparation_protocol_titles:
    - "Cryo-vitrification"

specimen_tracks:
  patterns:
    - "tomo_(\\d{4})"

datasets:
  - name: "Tilt series stacks"
    images:
      by_type:
        tilt_series: "**/*.mrc.st"
    specimen_tracks:
      image_acquisition_protocol_title:
        dataset:
          - "Cryo-ET"

  - name: "Reconstructed tomograms"
    images:
      by_type:
        tomogram: "**/*.mrc"
        segmentation: "**/*_segmentation.mrc"
    specimen_tracks:
      protocol_titles:
        tomogram:
          - "Tomogram reconstruction"
      annotation_method_titles:
        segmentation:
          - "Manual segmentation"
      specimen_groups:
        - specimen_ids: ["0023", "0024"]
          biosample_title: "Yeast cells (mutant strain)"
```

**What happens:**

1. REMBI entities are added to the metadata graph (protocols first, then
   biosamples, SIPPs, IAPs, annotation methods).
2. For each named dataset, files matching the `by_type` patterns are marked
   as `bia:Image` in the file list.
3. Specimen track identification:
   a. Image-assigned rows from datasets with `images.by_type` or typed
      `additional_files.images` entries are collected.
   b. The `by_type` patterns classify each file as a specific `ImageType`
      (e.g. `tilt_series`, `tomogram`, `segmentation`) for
      track-identification purposes only — this classification is not written
      to the file list.
   c. The top-level `specimen_tracks` regex patterns (or alias mappings)
      extract a specimen ID from each file path.
   d. Files are grouped into per-specimen `SpecimenTrack` objects, spanning
      all datasets.
4. Per-specimen metadata is resolved: `specimen_defaults` provides the
   baseline, overridden by any matching `specimen_groups` entries.
5. For each specimen, a `Specimen` entity is added to the metadata graph.
6. Track image labels are written to the file-list label/name column, and the
   `associated_source_image` column is populated: each
   non-track-start image (e.g. a tomogram) receives the label of its
   upstream image (e.g. the tilt series for the same specimen).
7. `associated_subject` is written for the track-start image rows, pointing
   to the generated Specimen entity.
8. IAP and protocol references are added to each Dataset entity in the
   graph from the per-dataset `specimen_tracks` config, and protocol
   references may also be written to image rows where configured by image type.
9. AnnotationMethod references from `annotation_method_titles` are added to the
   Dataset entity and written to `associated_annotation_method` for matching
   image rows, such as segmentation images.
