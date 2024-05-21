from bia_ingest.conversion import (
    generate_biosample_uuid,
    generate_specimen_uuid,
    generate_image_acquisition_uuid,
)
from bia_integrator_api.models.biosample import Biosample
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.models.image_acquisition import ImageAcquisition


def create_expected_biosample(accession_id):
    """ Create Biosample

    """
    title = "Test Biosample "

    organism_scientific_name = "Homo sapiens"
    organism_common_name = "human"
    organism_ncbi_taxon = ""

    description = 'Test description ("with some escaped chars") '

    intrinsic_variable = "Test intrinsic variable\nwith escaped character"
    extrinsic_variable = "Test extrinsic variable"
    expected_biosample_dict = {
        "accession_id": accession_id,
        "accno": "Biosample-1",
        "version": 0,
        "title": title,
        "organism_scientific_name": organism_scientific_name,
        "organism_common_name": organism_common_name,
        "organism_ncbi_taxon": organism_ncbi_taxon,
        "biological_entity": "Test biological entity",
        "description": description,
        "intrinsic_variables": [intrinsic_variable,],
        "extrinsic_variables": [extrinsic_variable,],
        "experimental_variables": ["Test experimental entity",],
    }
    expected_biosample_uuid = generate_biosample_uuid(expected_biosample_dict)
    expected_biosample_dict["uuid"] = expected_biosample_uuid
    expected_biosample = Biosample(**expected_biosample_dict)
    return expected_biosample


def create_expected_specimen(accession_id, expected_biosample_uuid=None):
    """Create Specimen

    """

    title = "Test specimen"
    sample_preparation_protocol = "Test sample preparation protocol"
    growth_protocol = "Test growth protocol"
    if not expected_biosample_uuid:
        expected_biosample_uuid = create_expected_biosample(accession_id).uuid

    expected_specimen_dict = {
        "accession_id": accession_id,
        "accno": "Specimen-2",
        "version": 0,
        "biosample_uuid": expected_biosample_uuid,
        "title": title,
        "sample_preparation_protocol": sample_preparation_protocol,
        "growth_protocol": growth_protocol,
    }
    expected_specimen_uuid = generate_specimen_uuid(expected_specimen_dict)
    expected_specimen_dict["uuid"] = expected_specimen_uuid
    expected_specimen = Specimen(**expected_specimen_dict)
    return expected_specimen


def create_expected_image_acquisition(accession_id, expected_specimen_uuid=None):
    """ Create Image Acquisition object directly as we do not need its dict

    """
    title = "Test Primary Screen Image Acquisition"
    imaging_instrument = "Test imaging instrument"
    image_acquisition_parameters = "Test image acquisition parameters"
    imaging_method = "confocal microscopy"

    if not expected_specimen_uuid:
        expected_specimen_uuid = create_expected_specimen(accession_id).uuid

    expected_image_acquisition_dict = {
        "accession_id": accession_id,
        "accno": "Image acquisition-3",
        "version": 0,
        "specimen_uuid": expected_specimen_uuid,
        "title": title,
        "imaging_instrument": imaging_instrument,
        "image_acquisition_parameters": image_acquisition_parameters,
        "imaging_method": imaging_method,
    }
    expected_image_acquisition_uuid = generate_image_acquisition_uuid(
        expected_image_acquisition_dict
    )
    expected_image_acquisition_dict["uuid"] = expected_image_acquisition_uuid
    expected_image_acquisition = ImageAcquisition(**expected_image_acquisition_dict)
    return expected_image_acquisition
