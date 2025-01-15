from bia_shared_datamodels.uuid_creation import create_study_uuid

accession_id = "S-BIADTEST"
accession_id_default = "S-BSSTTEST"

study_uuid = create_study_uuid(accession_id)
study_uuid_default = create_study_uuid(accession_id_default)
