## Description
This sub-package allows running bia-export for a set of accession ids one accession id at a time using nextflow. It can therefore be run locally if nextflow is installed or on a slurm cluster.

## Setup

1. Install nextflow if not present - see [https://www.nextflow.io/docs/latest/install.html](https://www.nextflow.io/docs/latest/install.html) or if on a slurm cluster try `module load nextflow`
2. Navigate to your working directory and:
    1. Copy `set_local_env.sh_template` -> `./set_local_env.sh` and modify as necessary.
    2. Copy `nextflow.config_template` -> `./nextflow.config` and comment out the `slurm` block if running locally
    3. Create a tmp directory as a sub directory of your working directory. Results will be saved here

## Usage
1. Navigate to your working directory (where `nextflow.config` was copied to)
2. Create a manifest of the form study_uuid:accession_id and save as `./tmp/manifest.txt`. E.g.
```
00357b15-5a36-48e3-ab9d-9af5b697afef:S-BSST445
0077e2c7-567a-46fa-8848-f39a86894755:S-BIAD851
0086e8f0-8c99-4fd2-8971-833c147443c8:S-BIAD821
00da4466-84cd-484e-adf5-2520c9c8ff0c:S-BIAD465
```
3. Set up the local environment: `source ./set_local_env.sh`
4. Run export: `nextflow run $BIA_EXPORT_DIR/nextflow/run_bia_export.nf`. Or `nextflow run $BIA_EXPORT_DIR/nextflow/run_bia_export.nf -c <path-to-nextflow.config>` if `nextflow.config` is not in the current directory.
5. Merge exported files: `poetry --directory $BIA_EXPORT_DIR run python $BIA_EXPORT_DIR/scripts/combine_export_files.py combine-export-files $BASEDIR/tmp/manifest.txt`. This produces `bia-study-metadata.json, bia-dataset-metadata.json, bia-image-export.json` in the `./tmp` directory
