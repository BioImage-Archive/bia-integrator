"""Utility functions for mock objects"""

accession_id = "S-BIADTEST"

# TODO: Move commented out functions for imaging to bia-converter-light
# def get_test_image() -> (
#    List[bia_data_model.Image]
# ):
#    image_acquisition_protocol_uuids = [str(iap.uuid) for iap in get_test_image_acquisition_protocol()]
#    specimen_uuids = [
#        str(specimen.uuid)
#        for specimen in get_test_specimen_for_experimentally_captured_image()
#    ]
#    experimental_imaging_dataset_uuids = [
#        str(eid.uuid) for eid in get_test_experimental_imaging_dataset()
#    ]
#    experimentally_captured_image_dicts = [
#        {
#            "path": "study_component1/im06.png",
#            "acquisition_process_uuid": image_acquisition_protocol_uuids,
#            "submission_dataset_uuid": experimental_imaging_dataset_uuids[0],
#            # TODO: All details from all associations have to be made
#            # into a single bia_data_model.Specimen - see clickup ticket
#            # https://app.clickup.com/t/8695fqxpy
#            # For now just storing uuid of specimen for first association
#            "subject_uuid": specimen_uuids[0],
#            "attribute": {
#                "AnnotationsIn": "ann06-10.json",
#                "metadata1_key": "metadata1_value",
#                "metadata2_key": "metadata2_value",
#            },
#        },
#        {
#            "path": "study_component1/im08.png",
#            "acquisition_process_uuid": image_acquisition_protocol_uuids,
#            "submission_dataset_uuid": experimental_imaging_dataset_uuids[0],
#            "subject_uuid": specimen_uuids[0],
#            "attribute": {
#                "AnnotationsIn": "ann06-10.json",
#                "metadata3_key": "metadata3_value",
#                "metadata4_key": "metadata4_value",
#            },
#        },
#        {
#            "path": "study_component2/im06.png",
#            "acquisition_process_uuid": [
#                image_acquisition_protocol_uuids[0],
#            ],
#            "submission_dataset_uuid": experimental_imaging_dataset_uuids[1],
#            "subject_uuid": specimen_uuids[1],
#            "attribute": {
#                "AnnotationsIn": "ann06-10.json",
#                "metadata1_key": "metadata1_value",
#                "metadata2_key": "metadata2_value",
#            },
#        },
#        {
#            "path": "study_component2/im08.png",
#            "acquisition_process_uuid": [
#                image_acquisition_protocol_uuids[0],
#            ],
#            "submission_dataset_uuid": experimental_imaging_dataset_uuids[1],
#            "subject_uuid": specimen_uuids[1],
#            "attribute": {
#                "AnnotationsIn": "ann06-10.json",
#                "metadata3_key": "metadata3_value",
#                "metadata4_key": "metadata4_value",
#            },
#        },
#    ]
#
#    experimentally_captured_images = []
#    attributes_to_consider = [
#        "path",
#        "acquisition_process_uuid",
#        "submission_dataset_uuid",
#        "subject_uuid",
#    ]
#    for eci in experimentally_captured_image_dicts:
#        eci["uuid"] = dict_to_uuid(eci, attributes_to_consider)
#        eci["version"] = 0
#        eci.pop("path")
#        experimentally_captured_images.append(
#            bia_data_model.ExperimentallyCapturedImage.model_validate(eci)
#        )
#
#    return experimentally_captured_images
#
#
# def get_test_image_annotation_dataset() -> List[bia_data_model.ImageAnnotationDataset]:
#    study_uuid = dict_to_uuid(
#        {
#            "accession_id": accession_id,
#        },
#        attributes_to_consider=[
#            "accession_id",
#        ],
#    )
#
#    attributes_to_consider = [
#        "accession_id",
#        "accno",
#        "title_id",
#    ]
#
#    image_annotation_dataset_info = [
#        {
#            "accno": "Annotations-29",
#            "accession_id": accession_id,
#            "title_id": "Segmentation masks",
#            "example_image_uri": [],
#            "submitted_in_study_uuid": study_uuid,
#            "version": 0,
#            "attribute": {},
#        },
#    ]
#
#    image_annotation_dataset = []
#    for image_annotation_dataset_dict in image_annotation_dataset_info:
#        image_annotation_dataset_dict["uuid"] = dict_to_uuid(
#            image_annotation_dataset_dict, attributes_to_consider
#        )
#        image_annotation_dataset_dict = filter_model_dictionary(
#            image_annotation_dataset_dict, bia_data_model.ImageAnnotationDataset
#        )
#        image_annotation_dataset.append(
#            bia_data_model.ImageAnnotationDataset.model_validate(
#                image_annotation_dataset_dict
#            )
#        )
#    return image_annotation_dataset
