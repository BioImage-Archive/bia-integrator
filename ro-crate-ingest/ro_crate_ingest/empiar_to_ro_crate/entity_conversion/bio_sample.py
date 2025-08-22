from bia_shared_datamodels.ro_crate_models import BioSample, Taxon
from ro_crate_ingest.empiar_to_ro_crate.entity_conversion.taxon import (
    get_taxon_under_biosample,
)
import logging

logger = logging.getLogger("__main__." + __name__)


def get_bio_samples_and_taxons(
    rembi_yaml: dict,
) -> tuple[list[BioSample], dict[str, Taxon]]:
    yaml_bio_samples = rembi_yaml.get("rembis", {}).get("BioSample", [])

    bio_samples = []
    taxons_dict = {}
    for yaml_bio_sample in yaml_bio_samples:

        get_taxon_under_biosample(yaml_bio_sample, taxons_dict)

        bio_samples.append(get_bio_sample(yaml_bio_sample))

    return bio_samples, taxons_dict


def get_bio_sample(bio_sample_dict: dict) -> BioSample:

    model_dict = {
        "@id": f"_:{bio_sample_dict["title"]}",
        "@type": ["bia:BioSample"],
        "title": bio_sample_dict["title"],
        "biologicalEntityDescription": bio_sample_dict.get(
            "biological_entity_description", ""
        ),
        "intrinsicVariableDescription": [],
        "extrinsicVariableDescription": [],
        "experimentalVariableDescription": [],
        "organismClassification": [
            {"@id": taxon["ncbi_id"]}
            for taxon in bio_sample_dict["organism_classification"]
        ],
        "growthProtocol": None,
    }

    return BioSample(**model_dict)
