## Image conversion workflow
The [assign_and_convert_images.sh](assign_and_convert_images.sh) bash script runs cli tools that perform the steps needed for the conversion of images in a study and uploads the converted images to S3

### Usage
Assumes user is in this directory
1. Copy the `set_local_env_template.sh` file to `set_local_env.sh`
2. Edit the values of the environment variables in `set_local_env.sh` as necessary
3. `source set_local_env.sh`
4. `source assign_and_convert_images.sh S-BIAD1423` ([S-BIAD1423](https://www.ebi.ac.uk/biostudies/BioImages/studies/S-BIAD1423) is a nice small study for testing image conversion).

### ToDo
Create nextflow script to run workflow
