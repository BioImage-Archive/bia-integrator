from bia_embed.cli import study

def test_study(existing_study):
    study(accno=[existing_study.accession_id])
