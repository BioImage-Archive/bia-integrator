Ingesting and converting
========================

Here we explain how the process of creating a BIA Study from an existing (public) BioStudies entry works.

To start, run the initial ingest:

    python scripts/ingest_from_biostudies.py S-BIAD610

This will create the study record, and assign identifiers to each file in the study.

Files recorded are then viewable with:

    % biaint filerefs list S-BIAD610
    f686ae3f-38f0-4250-9ce1-282a38f1565c BT474.tif 110121336
    7694297f-9876-4ee6-bf2a-f0a1f184b94c HT6.tif 452452027 

Which shows that we now have two file references. We currently do not know anything about images in the study:

    % biaint images list S-BIAD610

We can create an image from one of those file references with:

    python scripts/assign_single_image_from_fileref.py S-BIAD610 f686ae3f-38f0-4250-9ce1-282a38f1565c

The study now has an associated image:

    % biaint images list S-BIAD610
    defc458d-bec7-4df3-9aed-c526c5c05a30 BT474.tif fire_object

This shows the identifier, the short name (in this case original filename) and available representations (in this case fire_object) for the image.

biaint aliases add S-BIAD610 defc458d-bec7-4df3-9aed-c526c5c05a30 IM1

    % biaint aliases list-for-study S-BIAD610
    IM1 S-BIAD610 defc458d-bec7-4df3-9aed-c526c5c05a30




