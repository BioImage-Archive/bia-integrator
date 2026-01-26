from bia_shared_datamodels import ro_crate_models
from collections.abc import Iterable
from ro_crate_ingest.empiar_to_ro_crate.empiar.entry_api_models import Entry


def get_study(
    accession_id: str,
    empiar_api_entry: Entry,
    contributors: list[ro_crate_models.Contributor],
    datasets: Iterable[ro_crate_models.Dataset],
) -> ro_crate_models.Study:

    has_part_items = [{"@id": "file_list.tsv"}] 
    has_part_items.extend([{"@id": d.id} for d in datasets]) 

    study_dict = {
        "@id": "./",
        "@type": ["Dataset", "bia:Study"],
        "accessionId": accession_id,
        "name": empiar_api_entry.title,
        "license": "https://creativecommons.org/publicdomain/zero/1.0/",
        "datePublished": empiar_api_entry.release_date,
        "description": "",  # RO-Crate root objects must has a description
        "acknowledgement": None,
        "keyword": [],
        "contributor": [{"@id": c.id} for c in contributors],
        "hasPart": has_part_items, 
    }

    return ro_crate_models.Study(**study_dict)
