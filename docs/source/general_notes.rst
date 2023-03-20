export ACCESSION_ID=S-BIAD629
python scripts/ingest_from_biostudies.py $ACCESSION_ID
biaint filerefs list $ACCESSION_ID | head
python scripts/assign_single_image_from_fileref.py $ACCESSION_ID ba476a76-94dd-4ead-b8c4-d40c988d20de
biaint images list $ACCESSION_ID
python scripts/convert_to_zarr_and_upload.py $ACCESSION_ID bbf2e6cf-476b-4fd9-9263-5bea0b8432a3

Can now test with:
python scripts/generate_image_page.py $ACCESSION_ID bbf2e6cf-476b-4fd9-9263-5bea0b8432a3 > tmp/test.html


biaint filerefs list EMPIAR-11380
python scripts/assign_single_image_from_fileref.py EMPIAR-11380 1bd6ce34-6699-4633-89d2-757ed8341384
python scripts/assign_single_image_from_fileref.py EMPIAR-11380 b0b4f961-f6f3-4f8d-a049-76f9911ee74d
(nuclei labels)

% biaint images list EMPIAR-11380
52aa543c-659a-4522-bd37-cbfa4764dd17 /empiar/world_availability/11380/data/F107_A1_bin2_nuclei.mrc fire_object
5aec07ee-df5d-4ea4-ac32-fa55419464d6 /empiar/world_availability/11380/data/F107_A1_bin2.mrc fire_object

export ACCESSION_ID=EMPIAR-11380
export IMAGE_ID=52aa543c-659a-4522-bd37-cbfa4764dd17
mkdir -p converted/$ACCESSION_ID/$IMAGE_ID
mv test_image.zarr converted/$ACCESSION_ID/$IMAGE_ID/$IMAGE_ID.zarr
mv test_mask.zarr converted/$ACCESSION_ID/$IMAGE_ID/$IMAGE_ID.zarr

aws --region us-east-1 --endpoint-url https://uk1s3.embassy.ebi.ac.uk s3 sync converted/$ACCESSION_ID s3://bia-integrator-data/$ACCESSION_ID --acl public-read
echo https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/$ACCESSION_ID/$IMAGE_ID/$IMAGE_ID.zarr


Work this out from filerefs in study:

https://ftp.ebi.ac.uk/empiar/world_availability/11380/data/F107_A1_bin2_nuclei.mrc

--

EMPIAR-10982
7560cbea-aa51-4912-9506-195bef1ce2b5 mito_benchmarks/glycolytic_muscle/glycolytic_muscle_em.tif 88534712
9cbb9ef8-b29d-494a-9dd9-236b43ae206f mito_benchmarks/glycolytic_muscle/glycolytic_muscle_mito.tif 88534712

Unzip-and-copy pipeline
-----------------------

export ACCESSION_ID=S-BIAD628
biaint images list $ACCESSION_ID
python scripts/zipped_zarr_to_ngff.py $ACCESSION_ID 6fa9b973-3caf-46df-b1f3-d0fe8a24f665
