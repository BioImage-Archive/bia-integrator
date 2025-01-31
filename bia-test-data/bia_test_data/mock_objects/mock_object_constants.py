from bia_shared_datamodels.uuid_creation import create_study_uuid

accession_id = "S-BIADTEST"
accession_id_biostudies_default = "S-BSSTTEST"

study_uuid = create_study_uuid(accession_id)
study_uuid_biostudies_default = create_study_uuid(accession_id_biostudies_default)
