EMPIAR conversion
=================

bash ~/mount-empiar-fire.sh

ls /hps/nobackup/matthewh/matthewh/empiar-fire-mount/world_availability/


EMPIAR-10310
FIB-SEM of parapodia from Platynereis dumerilii

singularity exec /nfs/production/matthewh/bia.sif conda run -n bia /opt/conda/envs/bia/bin/bioformats2raw


cp /hps/nobackup/matthewh/matthewh/empiar-fire-mount/world_availability/10310/data/20180813_platynereis_parapodia/sift_aligned/slice_0001.tif .

Copy timings:

100 slices - 3 min

Conversion:

100 slices: real	1m15.518s
200 slices: 1m48.612s
300 slices: 3m14.736s

time singularity exec /nfs/production/matthewh/bia.sif conda run -n bia /opt/conda/envs/bia/bin/bioformats2raw local.pattern test.zarr

Copy to S3:

ACCESSION_ID=EMPIAR-10310
IMAGE_ID=IM1

aws --region us-east-1 --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 sync EMPIAR-10310 s3://bia-integrator-data/EMPIAR-10310 --acl public-read

https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/EMPIAR-10310/IM1/IM1.zarr/0

Converting an EMPIAR entry
--------------------------

Copying from FIRE to codon
~~~~~~~~~~~~~~~~~~~~~~~~~~

export ACCESSION_NO=10903
bsub -Is -q datamover bash
cd /hps/nobackup/matthewh/matthewh/
mkdir file-cache/EMPIAR-$ACCESSION_NO

source ~/miniconda3/bin/activate
aws --no-sign-request --endpoint https://hl.fire.sdo.ebi.ac.uk/ s3 ls s3://imaging-public/world_availability/$ACCESSION_NO/data/

Determine which folder/imageset to convert, then:

export IMAGESET=20140801_hela-wt_xy5z8nm_as/
aws --no-sign-request --endpoint https://hl.fire.sdo.ebi.ac.uk/ s3 sync s3://imaging-public/world_availability/$ACCESSION_NO/data/$IMAGESET file-cache/EMPIAR-$ACCESSION_NO/

or copy everything:

aws --no-sign-request --endpoint https://hl.fire.sdo.ebi.ac.uk/ s3 sync s3://imaging-public/world_availability/$ACCESSION_NO/data/ file-cache/EMPIAR-$ACCESSION_NO/

Conversion
~~~~~~~~~~

Using a pattern
~~~~~~~~~~~~~~~

bsub -Is bash
cd /hps/nobackup/matthewh/matthewh/

export a suitable pattern:

echo "file-cache/EMPIAR-$ACCESSION_NO/slice_<0000-1726>.tif" > $ACCESSION_NO.pattern

mkdir -p converted/EMPIAR-$ACCESSION_NO/IM1
time singularity exec /nfs/production/matthewh/bia.sif conda run -n bia /opt/conda/envs/bia/bin/bioformats2raw $ACCESSION_NO.pattern converted/EMPIAR-$ACCESSION_NO/IM1/IM1.zarr

No pattern needed:

bsub -Is bash
cd /hps/nobackup/matthewh/matthewh/
mkdir -p converted/EMPIAR-$ACCESSION_NO/IM1
export FILENAME=stack03_ESB_50_4200_TM1b_cr_r05_ibc_8b.tif
time singularity exec /nfs/production/matthewh/bia.sif conda run -n bia /opt/conda/envs/bia/bin/bioformats2raw file-cache/EMPIAR-$ACCESSION_NO/$FILENAME converted/EMPIAR-$ACCESSION_NO/IM1/IM1.zarr





Uploading to Embassy (full automation)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

bsub -Is -q datamover bash
cd /hps/nobackup/matthewh/matthewh/
source ~/miniconda3/bin/activate
aws --region us-east-1 --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 sync converted/EMPIAR-$ACCESSION_NO s3://bia-integrator-data/EMPIAR-$ACCESSION_NO --acl public-read
echo https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/EMPIAR-$ACCESSION_NO/IM1/IM1.zarr/0


Meanwhile...
------------

In bia-integrator-tools:

vim EMPIAR-11275.yml

Check to converted file:

https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/EMPIAR-11275/IM1/IM1.zarr/0

Then:
export ACCESSION_NO=10311
python scripts/study_from_empiar.py local-data/EMPIAR-$ACCESSION_NO.yml
python scripts/register_ome_ngff_rep.py EMPIAR-$ACCESSION_NO IM1 https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/EMPIAR-$ACCESSION_NO/IM1/IM1.zarr/0
python scripts/extract_ome_metadata.py EMPIAR-$ACCESSION_NO IM1
python scripts/omero_info_rewriter.py EMPIAR-$ACCESSION_NO IM1
python scripts/annotate_study_from_zarr.py EMPIAR-$ACCESSION_NO
python scripts/run_post_conversion_annotation.py EMPIAR-$ACCESSION_NO
python scripts/generate_representative_image_and_set_to_default.py EMPIAR-$ACCESSION_NO IM1
biaint collections add-study empiar EMPIAR-$ACCESSION_NO

With new architecture
---------------------

biaint filerefs list EMPIAR-11380

% python scripts/assign_single_image_from_fileref.py EMPIAR-11380 e2aef854-0ce3-4e28-9fff-df6b7f20b7e5
INFO:/Users/matthewh/projects/bia-integrator-tools/scripts/assign_single_image_from_fileref.py:Assigned name /empiar/world_availability/11380/data/F107_A1_bin2_actin.mrc
INFO:bia_integrator_core.image:Writing image to /Users/matthewh/.bia-integrator-data/images/EMPIAR-11380/a7c25fbf-0e40-4f7a-87c7-7798a05f2a4f.json

biaint images list EMPIAR-11380
python scripts/stage_files.py EMPIAR-11380 a7c25fbf-0e40-4f7a-87c7-7798a05f2a4f fire_object