# Set base for dirs containing scripts and cli commands
export BIA_ASSIGN_IMAGE_DIR=PATH_TO/bia-integrator/bia-assign-image
export BIA_CONVERTER_DIR=PATH_TO/bia-integrator/bia-converter

# For bia-integrator-api
export BIA_API_BASEPATH="https://wwwdev.ebi.ac.uk/bioimage-archive/api"
export BIA_API_USERNAME='test@example.com'
export BIA_API_PASSWORD='test'
export api_base_url=$BIA_API_BASEPATH
# bia-assign-image uses the settings class to determine whether to use the prod or local API
# API_PROFILE below sets this when calling its cli. Possible values are 'prod' or 'local'
export API_PROFILE=prod

# For storing downloaded files and intermediate conversions
export cache_root_dirpath=/home/test/.cache/bia-converter

# For convert_to_zarr with bioformats2raw
export bioformats2raw_bin=PATH_TO_BIOFORMATS_TO_RAW_BINARY/bin/bioformats2raw
export bioformats2raw_java_home=PATH_TO_ENV_FOR_BIOFORMATS_TO_RAW e.g. /home/test/miniconda3/envs/bia

# For upload to Embassy S3
export EMBASSY_S3="https://uk1s3.embassy.ebi.ac.uk"
export bucket_name="bia-integrator-data"
# Use testbucket-bia bucket for testing
# export bucket_name="testbucket-bia"
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
