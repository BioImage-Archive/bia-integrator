from bia_embed.cli import study, delete_for_model
from bia_integrator_api.models.study import Study

def test_study(existing_study: Study):
    study(accno=[existing_study.accession_id])

def test_delete_for_model(existing_study: Study):
    study(accno=[existing_study.accession_id])
    delete_for_model(model="sentence-transformers/all-roberta-large-v1")

    # re-creating to check that the embedding was deleted
    study(accno=[existing_study.accession_id])