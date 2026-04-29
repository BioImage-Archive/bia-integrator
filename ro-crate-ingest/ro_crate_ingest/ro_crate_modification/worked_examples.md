## Worked example: a single file through Scenario 3

This traces one file — a reconstructed tomogram — from its row in the
minimal RO-Crate file list all the way to a fully-described entry in the
enriched RO-Crate, using the Scenario 3 config above.

### Starting point: the minimal RO-Crate

The minimal RO-Crate for EMPIAR-12345 contains:

- A `Study` entity at `./`
- Two `Dataset` entities, one per EMPIAR imageset:
  - `@id: "#Tilt%20series%20stacks"`, `name: "Tilt series stacks"`
  - `@id: "#Reconstructed%20tomograms"`, `name: "Reconstructed tomograms"`
- A `FileList` entity pointing to `file_list.tsv`

The file list (`file_list.tsv`) has these columns at the minimal stage:

| file_path | size_in_bytes | dataset |
|---|---|---|
| `data/TS/tomo_0042.mrc.st` | 4200000 | `#Tilt%20series%20stacks` |
| `data/Tomo/tomo_0042.mrc` | 18000000 | `#Reconstructed%20tomograms` |
| `data/TS/tomo_0023.mrc.st` | 4100000 | `#Tilt%20series%20stacks` |
| `data/Tomo/tomo_0023.mrc` | 17500000 | `#Reconstructed%20tomograms` |
| `data/README.txt` | 1200 | _(null)_ |

No `type` or `associated_source_image` columns exist yet.


### Step 1: REMBI entities added

The enricher processes `rembis` in order: protocols first, then biosamples.

The following entities are added to the RO-Crate metadata graph:

```
Protocol         @id: "#Yeast%20culture%20protocol"
Protocol         @id: "#Tomogram%20reconstruction"
Taxon            @id: "#Saccharomyces%20cerevisiae"
BioSample        @id: "#Yeast%20cells"
                   biologicalEntityDescription: "S. cerevisiae BY4741"
                   organismClassification: [{"@id": "#Saccharomyces%20cerevisiae"}]
                   growthProtocol: {"@id": "#Yeast%20culture%20protocol"}
SIPP             @id: "#Cryo-vitrification"
IAP              @id: "#Cryo-ET"
```

The `#Yeast%20culture%20protocol` entity is added before `#Yeast%20cells` so
that the `growthProtocol` reference is valid when the BioSample is added.


### Step 2: Image assignment — "Tilt series stacks"

The config for this dataset is:

```yaml
- name: "Tilt series stacks"
  images:
    by_type:
      tilt_series: "**/*.mrc.st"
```

The enricher:

1. Resolves `"Tilt series stacks"` → `@id: "#Tilt%20series%20stacks"`.
2. Filters the file list to rows where `dataset == "#Tilt%20series%20stacks"`.
3. Adds a `type` column to the file list (it didn't exist yet).
4. Both files match `**/*.mrc.st` → `type` set to `bia:Image`.

File list after this step:

| file_path | size_in_bytes | dataset | type |
|---|---|---|---|
| `data/TS/tomo_0042.mrc.st` | 4200000 | `#Tilt%20series%20stacks` | `bia:Image` |
| `data/Tomo/tomo_0042.mrc` | 18000000 | `#Reconstructed%20tomograms` | _(null)_ |
| `data/TS/tomo_0023.mrc.st` | 4100000 | `#Tilt%20series%20stacks` | `bia:Image` |
| `data/Tomo/tomo_0023.mrc` | 17500000 | `#Reconstructed%20tomograms` | _(null)_ |
| `data/README.txt` | 1200 | _(null)_ | _(null)_ |


### Step 3: Image assignment — "Reconstructed tomograms"

Both `tomo_0042.mrc` and `tomo_0023.mrc` match `**/*.mrc` → `type` set to
`bia:Image`.

File list after this step:

| file_path | size_in_bytes | dataset | type |
|---|---|---|---|
| `data/TS/tomo_0042.mrc.st` | 4200000 | `#Tilt%20series%20stacks` | `bia:Image` |
| `data/Tomo/tomo_0042.mrc` | 18000000 | `#Reconstructed%20tomograms` | `bia:Image` |
| `data/TS/tomo_0023.mrc.st` | 4100000 | `#Tilt%20series%20stacks` | `bia:Image` |
| `data/Tomo/tomo_0023.mrc` | 17500000 | `#Reconstructed%20tomograms` | `bia:Image` |
| `data/README.txt` | 1200 | _(null)_ | _(null)_ |

`README.txt` is untouched: it belongs to no dataset and matches no pattern.


### Step 4: Default dataset

After all named datasets are processed, `README.txt` is still unassigned.
A `"Default dataset"` entity is created automatically and `README.txt` is
assigned to it. The default dataset is also added to the Study entity's
`hasPart` list.

Final file list after default assignment:

| file_path | size_in_bytes | dataset | type |
|---|---|---|---|
| `data/TS/tomo_0042.mrc.st` | 4200000 | `#Tilt%20series%20stacks` | `bia:Image` |
| `data/Tomo/tomo_0042.mrc` | 18000000 | `#Reconstructed%20tomograms` | `bia:Image` |
| `data/TS/tomo_0023.mrc.st` | 4100000 | `#Tilt%20series%20stacks` | `bia:Image` |
| `data/Tomo/tomo_0023.mrc` | 17500000 | `#Reconstructed%20tomograms` | `bia:Image` |
| `data/README.txt` | 1200 | `#Default%20dataset` | _(null)_ |

(Specimen track steps follow — see below.)


### Step 5a: Collecting image-assigned rows for track identification

Both datasets have `specimen_tracks` blocks, so all four image-assigned
rows are collected. The `by_type` patterns classify each file:

| file_path | dataset_name | image_type |
|---|---|---|
| `data/TS/tomo_0042.mrc.st` | `"Tilt series stacks"` | `tilt_series` |
| `data/TS/tomo_0023.mrc.st` | `"Tilt series stacks"` | `tilt_series` |
| `data/Tomo/tomo_0042.mrc` | `"Reconstructed tomograms"` | `tomogram` |
| `data/Tomo/tomo_0023.mrc` | `"Reconstructed tomograms"` | `tomogram` |

Note: the `image_type` column is internal to this step — it is not written
to the file list.


### Step 5b: Specimen ID extraction

The top-level `specimen_tracks` config uses:

```yaml
specimen_tracks:
  patterns:
    - "tomo_(\\d{4})"
```

The regex `tomo_(\d{4})` is applied to each file path:

- `data/TS/tomo_0042.mrc.st` → `"0042"`
- `data/TS/tomo_0023.mrc.st` → `"0023"`
- `data/Tomo/tomo_0042.mrc` → `"0042"`
- `data/Tomo/tomo_0023.mrc` → `"0023"`


### Step 5c: Track merging

`_merge_tracks` groups rows by specimen ID:

**SpecimenTrack for `"0042"`:**
```
tilt_series:  Path("data/TS/tomo_0042.mrc.st")
tomogram:     Path("data/Tomo/tomo_0042.mrc")
dataset_for:  {"tilt_series": "Tilt series stacks",
               "tomogram":    "Reconstructed tomograms"}
```

**SpecimenTrack for `"0023"`:**
```
tilt_series:  Path("data/TS/tomo_0023.mrc.st")
tomogram:     Path("data/Tomo/tomo_0023.mrc")
dataset_for:  {"tilt_series": "Tilt series stacks",
               "tomogram":    "Reconstructed tomograms"}
```


### Step 5d: Specimen metadata resolution

`specimen_defaults` provides the baseline. The `specimen_groups` entry
for `["0023", "0024"]` overrides `biosample_title` for specimen `"0023"`:

| specimen_id | biosample_title | sipp_titles |
|---|---|---|
| `"0042"` | `"Yeast cells"` | `["Cryo-vitrification"]` |
| `"0023"` | `"Yeast cells (mutant strain)"` | `["Cryo-vitrification"]` |


### Step 5e: Specimen and CreationProcess entities created

For specimen `"0042"`:

```json
{"@id": "#Specimen_0042", "@type": "bia:Specimen",
 "biologicalEntity": [{"@id": "#Yeast%20cells"}],
 "imagingPreparationProtocol": [{"@id": "#Cryo-vitrification"}]}

{"@id": "#CreationProcess_Specimen_0042", "@type": "bia:CreationProcess",
 "subject": {"@id": "#Specimen_0042"}}
```

For specimen `"0023"`, `biosample_title` is overridden:

```json
{"@id": "#Specimen_0023", "@type": "bia:Specimen",
 "biologicalEntity": [{"@id": "#Yeast%20cells%20%28mutant%20strain%29"}],
 "imagingPreparationProtocol": [{"@id": "#Cryo-vitrification"}]}
```

Note: `"Yeast cells (mutant strain)"` → `#Yeast%20cells%20%28mutant%20strain%29`
via `title_to_id` URL quoting. The referenced BioSample entity must itself
exist in the graph — declare it under `rembis.biosamples` if it differs
from the default.


### Step 5f: associated_source_image written to file list

For `tomogram` entries, the upstream is the tilt series (or frames if
present). Tilt series are track starts here, so they receive no label.

Final file list:

| file_path | size_in_bytes | dataset | type | associated_source_image |
|---|---|---|---|---|
| `data/TS/tomo_0042.mrc.st` | 4200000 | `#Tilt%20series%20stacks` | `bia:Image` | _(null)_ |
| `data/Tomo/tomo_0042.mrc` | 18000000 | `#Reconstructed%20tomograms` | `bia:Image` | `Specimen_0042 tilt_series` |
| `data/TS/tomo_0023.mrc.st` | 4100000 | `#Tilt%20series%20stacks` | `bia:Image` | _(null)_ |
| `data/Tomo/tomo_0023.mrc` | 17500000 | `#Reconstructed%20tomograms` | `bia:Image` | `Specimen_0023 tilt_series` |
| `data/README.txt` | 1200 | `#Default%20dataset` | _(null)_ | _(null)_ |


### Step 5g: Dataset entities updated with IAP and protocol references

`"Tilt series stacks"` → `associatedImageAcquisitionProtocol: [{"@id": "#Cryo-ET"}]`

`"Reconstructed tomograms"` → `associatedProtocol: [{"@id": "#Tomogram%20reconstruction"}]`


### Final RO-Crate metadata graph (new entities only)

```
Protocol                  #Yeast%20culture%20protocol
Protocol                  #Tomogram%20reconstruction
Taxon                     #Saccharomyces%20cerevisiae
BioSample                 #Yeast%20cells
SIPP                      #Cryo-vitrification
IAP                       #Cryo-ET
Specimen                  #Specimen_0042
Specimen                  #Specimen_0023
Dataset                   #Default%20dataset
```

Plus updates to existing entities:

```
Dataset #Tilt%20series%20stacks
  → associatedImageAcquisitionProtocol: [#Cryo-ET]

Dataset #Reconstructed%20tomograms
  → associatedProtocol: [#Tomogram%20reconstruction]

Study ./
  → hasPart includes #Default%20dataset
```
