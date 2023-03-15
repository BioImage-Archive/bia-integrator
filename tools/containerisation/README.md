# Containerisation of bia-integrator-tools

Docker container to allow running of BIA integrator tools via Docker or Singularity.

The docker image can be built locally from the Dockerfile or pulled from EBI's gitlab registry (restricted to EBI users).

## Building image locally
From directory with Dockerfile build the image.
```
docker build bia:v1.0 .
```

## Running from container registry
Because EBI's gitlab registry uses 2 factor authentication, you need to create a personal access token with a minimum scope of `read_registry` (see [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#personal-access-tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#personal-access-tokens) )

```bash
# login to EBI docker
# On first go:
docker login dockerhub.ebi.ac.uk -u <username> -p <personal access token>
# On subsequent goes (details should be stored in ~/.docker/config.json):
docker login dockerhub.ebi.ac.uk

# Pull the image
docker image pull dockerhub.ebi.ac.uk/bioimage-archive/study-explorer/fire-to-s3/bia:v1.0

# Prerequistes for running commands `data_dirpath` determines the local directory used to store artefacts downloaded from the BIA.
export data_dirpath=/home/kola/.bia-integrator-data
export bioformats2raw_java_home=/opt/conda/envs/bia
export bioformats2raw_bin=/opt/conda/envs/bia/bin/bioformats2raw

# You need AWS credentials for upload to Embassy S3 storage
export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXX

# Make reference to container an environment variable to cater for locally built version or version pulled from gitlab
# If pulled from gitlab
export CONT_NAME=dockerhub.ebi.ac.uk/bioimage-archive/study-explorer/fire-to-s3/bia:v1.0
# If built locally
export CONT_NAME=bia:v1.0

# All commands from bia-integrator-tools can be run. Some examples:

# Pull details for a study
docker container run --rm --mount type=bind,src=${data_dirpath},dst=/root/.bia-integrator-data $CONT_NAME conda run -n bia python bia-integrator-tools/scripts/bst_pulldown.py S-BIAD229

# List studies
docker container run --rm --mount type=bind,src=${data_dirpath},dst=/root/.bia-integrator-data $CONT_NAME conda run -n bia biaint studies list

# List images for a study
docker container run --rm --mount type=bind,src=${data_dirpath},dst=/root/.bia-integrator-data $CONT_NAME conda run -n bia biaint images list S-BIAD229

# Convert to zarr and upload to S3
docker container run --rm -e bioformats2raw_java_home=$bioformats2raw_java_home -e bioformats2raw_bin=$bioformats2raw_bin -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY --mount type=bind,src=${data_dirpath},dst=/root/.bia-integrator-data $CONT_NAME conda run -n bia python bia-integrator-tools/scripts/convert_to_zarr_and_upload.py S-BIAD229 IM6

```

## Running using singularity (assuming an interactive bsub shell node on codon)
Because we use 2 factor authentication, you need to create a personal access token with a minimum scope of `read_registry` (see [https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#personal-access-tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html#personal-access-tokens) )

```bash
# Create your working area e.g. and work from it
mkdir /hps/nobackup/matthewh/kola/singularity && cd /hps/nobackup/matthewh/kola/singularity

# Pull the image, when prompted for 'Docker Username' enter your ebi user name. e.g. kola. Use personal access token for password
singularity pull --docker-login docker://dockerhub.ebi.ac.uk/bioimage-archive/study-explorer/fire-to-s3/bia:v1.0

# If you get an error about space something like:
#     FATAL: While making image from oci registry: ... Write failed because No space left on device
#     FATAL ERROR:Failed to write to output filesystem
#
# Try creating a tmp dir for singularity and setting its location using SINGULARITY_TMPDIR e.g. then re-running the pull command
export SINGULARITY_TMPDIR=/hps/nobackup/matthewh/kola/singularity/tmp && mkdir $SINGULARITY_TMPDIR

# Prerequistes for running commands are the same as for Docker image. However, environment variables are available within the singularity image so directories do not have to be mounted.
export data_dirpath=/home/kola/.bia-integrator-data
export bioformats2raw_java_home=/opt/conda/envs/bia
export bioformats2raw_bin=/opt/conda/envs/bia/bin/bioformats2raw

# You need AWS credentials for upload to AWS. If you have a .aws/credentials file they can be picked up from there. Otherwise, create:
export AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXXXXXXX
export AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXX

# All commands from bia-integrator-tools can be run either by shelling into the container or by 'executing' the container:

# To shell into the container assuming you are in same dir as bia_v1.0.sif
singularity shell bia_v1.0.sif

# If in the singularity shell omit the 'singularity exec bia_v1.0.sif' parts

# Pull details for a study
singularity exec bia_v1.0.sif conda run -n bia python /bia/bia-integrator-tools/scripts/bst_pulldown.py S-BIAD229

# List studies
singularity exec bia_v1.0.sif conda run -n bia biaint studies list

# List images for a study
singularity exec bia_v1.0.sif conda run -n bia biaint images list S-BIAD229

# Convert to zarr and upload to S3
singularity exec bia_v1.0.sif conda run -n bia python /bia/bia-integrator-tools/scripts/convert_to_zarr_and_upload.py S-BIAD229 IM6

# Use LSF to run the conversion
bsub singularity exec bia_v1.0.sif conda run -n bia python /bia/bia-integrator-tools/scripts/convert_to_zarr_and_upload.py S-BIAD229 IM6

```
