from . import TEST_SAMPLE_DATA


def test_load_and_annotate():

    from bia_integrator_core.integrator import load_and_annotate_study

    accession_id = "S-BIAD144"

    bia_study = load_and_annotate_study(accession_id)

    assert bia_study.accession_id == accession_id
    assert bia_study.example_image_uri == "https://uk1s3.embassy.ebi.ac.uk/bia-integrator-data/S-BIAD144-example.png"