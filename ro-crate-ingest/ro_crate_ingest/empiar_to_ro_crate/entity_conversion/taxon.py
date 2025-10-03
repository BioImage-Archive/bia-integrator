from bia_shared_datamodels import ro_crate_models
import logging

logger = logging.getLogger("__main__." + __name__)


def get_taxon_under_biosample(
    bio_sample_yaml: dict,
    taxon_dict: dict,
) -> None:

    taxons_yaml: list[dict] = bio_sample_yaml.get("organism_classification", [])

    for taxon_yaml in taxons_yaml:
        if taxon_yaml["ncbi_id"] not in taxon_dict:
            taxon = get_taxon(taxon_yaml)
            taxon_dict[taxon.id] = taxon


def get_taxon(
    taxon_yaml: dict,
) -> ro_crate_models.Taxon:

    model_dict = {
        "@id": taxon_yaml["ncbi_id"],
        "@type": ["bia:Taxon"],
        "commonName": taxon_yaml["common_name"],
        "scientificName": taxon_yaml["scientific_name"],
    }

    return ro_crate_models.Taxon(**model_dict)
