# Notes on EMPIAR proposal generation

In EMPIAR–RO-Crate, a proposal yaml file is used to direct the conversion — REMBI information is supplied, and datasets and their constituent images/annotations defined. The purpose of proposal generation is to streamline the creation of those proposal documents, which can be very long, and even when short, are time-consuming to construct. After the CLI, proposal generation starts at [`empiar_proposal_generation.py`](empiar_proposal_generation.py), and all subsequent generation-specific code code is found in [`proposal_generation`](./proposal_generation/). Here is a guide for configuring a proposal generation. 

## Examples

Example configuration files, along with a template, can be found in [`proposal_configurations`](../../proposal_configurations/), a couple of levels up from this readme. Note that the configuration, as with the proposals, starts with the `accession_id` and `paper_doi`.

## REMBI components

In the configuration, we have blocks for the REMBIs:
- `biosamples`
- `specimen_imaging_preparation_protocols`
- `image_acquisition_protocols`
- `protocols`

The specification of information in these blocks is faily self-explanatory, given the templates and exmaples, and should be completed with reference to the entry and the associated paper. Specimen information is dealt with below.

## Specimens

Specimen information is split across three parts of the config: `specimens`, `specimen_defaults`, and `specimen_groups` (the last of which lives inside each dataset block). Together these control both how specimen IDs are extracted from entry's file paths and what metadata is assigned to each specimen.

### Identifying specimens: the `specimens` block

The `specimens` block defines how a specimen ID is extracted from each file path. Exactly one of three strategies may be used.

**`patterns`** is the simplest approach — a list of regex patterns, each of which must contain at least one capturing group. The first pattern that matches a file path wins, and the captured group becomes the specimen ID. If a pattern contains multiple capturing groups, the captured values are joined with `_`. For example:

```yaml
specimens:
  patterns:
    - "tomo_(\\d{4})"
```

**`pattern_alias_mappings`** handles cases where the same specimen appears under different naming schemes across datasets — for instance, raw frames named with a short ID and tilt series named with a zero-padded ID. The keys are canonical regex patterns (which must include a `\d{N}` group defining the target zero-padded length), and the values are lists of alias patterns to match against. When an alias matches, the captured value is transformed to match the canonical format. For example:

```yaml
specimens:
  pattern_alias_mappings:
    "(\\d{4})":
      - "TS_(\\d+)_"
      - "tomo(\\d+)\\."
```

A file matching `TS_12_` would be assigned specimen ID `0012`.

**`literal_alias_mappings`** is for cases where there is no algorithmic relationship between names — each canonical specimen ID is mapped directly to a list of glob patterns. Any file matching one of those globs is assigned that specimen ID. This is the right choice when the mapping is essentially a lookup table derived from the paper or the entry's notes. For example:

```yaml
specimens:
  literal_alias_mappings:
    "centrosome_01": ["**/20190429/**/TS_05*", "**/cent1.mrc"]
    "centrosome_02": ["**/20200309/**/TS_002*", "**/cent2.mrc"]
```

### Assigning specimen metadata: `specimen_defaults` and `specimen_groups`

Once specimen IDs are extracted, metadata is assigned to each specimen through a cascade: `specimen_defaults` provides a baseline that applies to all specimens, and `specimen_groups` (inside any dataset block) can override it for specific specimens.

`specimen_defaults` is optional. If provided, it sets the biosample and preparation protocol titles that all specimens will inherit unless overridden:

```yaml
specimen_defaults:
  biosample_title: "C. elegans embryonic cells"
  specimen_imaging_preparation_protocol_titles:
    - "Embryo dissociation and plunge freezing"
    - "Cryo-FIB milling"
```

`specimen_groups` entries sit inside a dataset block and override the defaults for a subset of specimens. Each entry must target specimens either by a list of explicit IDs or by a regex pattern, and must provide at least one metadata field to override:

```yaml
datasets:
  - name: "My dataset"
    ...
    specimen_groups:
      - specimen_ids: ["0001", "0002"]
        biosample_title: "Variant cell line"
      - specimen_id_pattern: "tomo_01\\d\\d"
        specimen_imaging_preparation_protocol_titles:
          - "Alternative preparation protocol"
```

`specimen_ids` and `specimen_id_pattern` are mutually exclusive within a single group. When resolving metadata for a specimen, an exact ID match takes precedence over a pattern match. Later dataset blocks take precedence over earlier ones for the same specimen.

## Frame pattern inference and `pattern_inference_delimiters`

When a dataset includes raw frames, the proposal generator automatically infers a file pattern for each specimen's frame collection by comparing filenames and replacing the parts that vary across frames with {}. 

For example, a set of files like:

raw_frames/b3g1_SR_ts50_101_0000_-15.0.tif
raw_frames/b3g1_SR_ts50_101_0001_-15.0.tif
raw_frames/b3g1_SR_ts50_101_0002_-15.0.tif

would produce the pattern raw_frames/b3g1_SR_ts50_101_{}_-15.0.tif.
The inference works by splitting each filename into tokens on a set of delimiter characters, then comparing token-by-token — tokens that are constant across all files are kept as-is, tokens that vary become {}. The delimiters themselves are preserved in the output pattern.

The default values for splitting tokens are `_` and `.`; for non-default values, put these in the configuration file:

```yaml
pattern_inference_delimiters:
  - "-"
  - ":"
```

## Datasets

Each entry in the `datasets` list produces exactly one dataset block in the output proposal, regardless of how many image types it covers. The required fields are `name` and `data_directories`; all others are optional.

### `data_directories`

Specifies which part of the file tree this dataset covers. Can be a single string or a list. Files are filtered to those whose paths start with one of these directories before any other processing.

```yaml
data_directories:
  - "data/Data_Set_1"
```

### `file_globs`

Controls how files within the dataset's directories are classified into image types. Keys must be valid image type names (`frames`, `tilt_series`, `aligned_tilt_series`, `tomogram`, `denoised_tomogram`); values are glob patterns or lists of glob patterns.

```yaml
file_globs:
  frames:
    - "**/raw_frames/*.tif"
  tilt_series:
    - "**/tilt_series/*.mrc"
  tomogram:
    - "**/tomo_rec_4bin_SART/*.mrc"
```

Files that match no glob are still claimed by the dataset (if they are within `data_directories` and have a resolvable specimen ID), but are not assigned an image type — they appear in the track's `extra_files` and are not included in any `assigned_images` output.

### `image_acquisition_protocol_title`

Associates an image acquisition protocol with images in this dataset. Supports two modes:

**Dataset-level** (the common case): the protocol is attached to the dataset block as a whole via `assigned_dataset_rembis`. Use the key `dataset`:

```yaml
image_acquisition_protocol_title:
  dataset:
    - "Cryo-electron tomography"
```

**Type-level**: the protocol is attached to individual `assigned_images` entries of a specific image type only. Use the image type name as the key:

```yaml
image_acquisition_protocol_title:
  frames: "Cryo-electron tomography"
```

### `protocol_titles`

Associates processing protocols with specific image types. These are attached per `assigned_images` entry. Keys are image type names; values are a single title or a list.

```yaml
protocol_titles:
  aligned_tilt_series:
    - "Dataset 1 pre-processing"
  tomogram:
    - "Tomogram reconstruction"
```

### `specimen_groups`

See the Specimens section above.
