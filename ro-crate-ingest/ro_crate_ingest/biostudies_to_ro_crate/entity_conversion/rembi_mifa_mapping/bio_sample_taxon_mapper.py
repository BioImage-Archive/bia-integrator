from collections import defaultdict
import logging
import re
from urllib.parse import quote

from bia_ro_crate.models import ro_crate_models
from bia_shared_datamodels.package_specific_uuid_creation import (
    biostudies_ingest_uuid_creation,
    shared,
)

from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_api import (
    Section,
    Submission,
)
from ro_crate_ingest.biostudies_to_ro_crate.biostudies.submission_parsing_utils import (
    attributes_to_dict,
    filter_section_by_attribute_key,
    find_sections_recursive,
)

from .base_mapper import Mapper

logger = logging.getLogger("__main__." + __name__)


class BioSampleTaxonMapper(Mapper):

    def __init__(self) -> None:
        self.taxon_bnode_int = 0
        self.unique_taxons_list: list[ro_crate_models.Taxon] = []
        super().__init__()

    def map(self, submission: Submission, association_map: dict[type, dict[str, str]]):

        if not submission.accno:
            raise ValueError("Missing accession id for study: cannot proccess.")

        specimen_info = self._get_biosample_specimen_association_pairs(submission)

        biosample_sections = filter_section_by_attribute_key(
            find_sections_recursive(submission.section, ["Biosample"], []),
            ["Title"],
        )

        for section in biosample_sections:
            referenced_taxon_ids = self._get_taxon_under_biosample(
                bio_sample_section=section,
            )

            attr_dict = attributes_to_dict(section.attributes)

            association_ref: str = attr_dict["title"]

            mapped_specimens = specimen_info[association_ref]

            for specimen_reference in mapped_specimens:
                # We expect there to be at least 1 specimen per biosample, but 0-1 growth protocols per specimen.
                growth_protocol_id = association_map[ro_crate_models.Protocol].get(
                    specimen_reference
                )

                bio_sample = self.get_bio_sample(
                    section, referenced_taxon_ids, growth_protocol_id, submission.accno
                )

                self.mapped_object.append(bio_sample)

                if growth_protocol_id:
                    association_map[ro_crate_models.BioSample][
                        f"{association_ref}{specimen_reference}"
                    ] = bio_sample.id
                else:
                    association_map[ro_crate_models.BioSample][
                        association_ref
                    ] = bio_sample.id

    def get_bio_sample(
        self,
        section: Section,
        referenced_taxon_ids: list[str],
        growth_protocol_id: str | None,
        accession_id: str,
    ) -> ro_crate_models.BioSample:
        attr_dict = attributes_to_dict(section.attributes)

        if growth_protocol_id:
            study_uuid = str(shared.create_study_uuid(accession_id)[0])
            protocol_uuid = str(
                biostudies_ingest_uuid_creation.create_protocol_uuid(
                    study_uuid, growth_protocol_id.removeprefix("#_")
                )[0]
            )
            id = "#" + quote(f"{section.accno} {protocol_uuid}")
        else:
            id = f"#{quote(section.accno)}"

        model_dict = {
            "@id": id,
            "@type": ["bia:BioSample"],
            "title": attr_dict["title"],
            "biologicalEntityDescription": attr_dict.get("biological entity", ""),
            "intrinsicVariableDescription": self._get_value_in_list_or_empty_list(
                attr_dict, "intrinsic variable"
            ),
            "extrinsicVariableDescription": self._get_value_in_list_or_empty_list(
                attr_dict, "extrinsic variable"
            ),
            "experimentalVariableDescription": self._get_value_in_list_or_empty_list(
                attr_dict, "experimental variable"
            ),
            "organismClassification": [
                {"@id": taxon_id} for taxon_id in referenced_taxon_ids
            ],
            "growthProtocol": (
                {"@id": growth_protocol_id} if growth_protocol_id else None
            ),
        }

        return ro_crate_models.BioSample(**model_dict)

    @staticmethod
    def _get_value_in_list_or_empty_list(attr_dict: dict, field_name: str) -> list:
        value = attr_dict.get(field_name, None)
        if value:
            return [value]
        else:
            return []

    def _get_taxon_under_biosample(
        self,
        bio_sample_section: Section,
    ) -> list[str]:
        referenced_taxon_id_list: list[str] = []

        sections = find_sections_recursive(bio_sample_section, ["Organism"])

        if len(sections) > 0:
            for section in sections:
                tx_info: dict = self._get_taxon_information_from_section(section)
                taxon_id, is_unique = self._get_taxon_id_and_uniqueness(tx_info)
                referenced_taxon_id_list.append(taxon_id)

                if is_unique:
                    taxon = self._get_ro_crate_taxon(taxon_id, tx_info)
                    self.unique_taxons_list.append(taxon)
                    self.mapped_object.append(taxon)

        else:
            tx_info: dict = self._get_taxon_information_from_biosample_attribute(
                bio_sample_section
            )
            taxon_id, is_unique = self._get_taxon_id_and_uniqueness(tx_info)
            referenced_taxon_id_list.append(taxon_id)
            if is_unique:
                taxon = self._get_ro_crate_taxon(taxon_id, tx_info)
                self.unique_taxons_list.append(taxon)
                self.mapped_object.append(taxon)

        return referenced_taxon_id_list

    def _get_taxon_information_from_section(
        self,
        section: Section,
    ) -> dict:
        attr_dict = attributes_to_dict(section.attributes)

        info_dict = {
            "ncbiId": attr_dict.get("ncbi taxon id", None),
            "scientificName": attr_dict.get("scientific name", ""),
            "commonName": attr_dict.get("common name", ""),
        }

        return info_dict

    def _get_taxon_information_from_biosample_attribute(
        self,
        bio_sample_section: Section,
    ):
        bio_sample_attr_dict = attributes_to_dict(bio_sample_section.attributes)

        organism: str = bio_sample_attr_dict.get("organism", "")
        try:
            organism_scientific_name, organism_common_name = organism.split("(")
            organism_common_name = organism_common_name.rstrip(")")
        except ValueError:
            organism_scientific_name = organism
            organism_common_name = ""

        info_dict = {
            "ncbiId": None,
            "commonName": organism_common_name.strip(),
            "scientificName": organism_scientific_name.strip(),
        }

        return info_dict

    @staticmethod
    def _get_ro_crate_taxon(
        taxon_id: str,
        taxon_info: dict,
    ) -> ro_crate_models.Taxon:
        model_dict = {
            "@id": taxon_id,
            "@type": ["bia:Taxon"],
            "commonName": taxon_info["commonName"],
            "scientificName": taxon_info["scientificName"],
        }

        return ro_crate_models.Taxon(**model_dict)

    def _get_taxon_id_and_uniqueness(
        self,
        taxon_info: dict,
    ) -> tuple[str, bool]:
        taxon_id = None
        is_unique = True

        if taxon_info["ncbiId"]:
            taxon_id = re.sub("^[^0-9]*", "NCBI:txid", taxon_info["ncbiId"])
            for tx in self.unique_taxons_list:
                if tx.id == taxon_id:
                    add_to_taxon_list = False

            return taxon_id, is_unique
        else:
            for tx in self.unique_taxons_list:
                if (
                    tx.commonName == taxon_info["commonName"]
                    and tx.scientificName == taxon_info["scientificName"]
                ):
                    taxon_id = tx.id
                    add_to_taxon_list = False
                    return taxon_id, add_to_taxon_list

            taxon_id = f"#tx{self.taxon_bnode_int}"
            self.taxon_bnode_int += 1
            return taxon_id, is_unique

    @staticmethod
    def _get_biosample_specimen_association_pairs(
        submission: Submission,
    ) -> dict[str, list[str]]:
        """
        Sets up a dictionary of the form:
        {
            <biosample reference>: [ <specimen 1 reference>, <specimen 2 reference> ]
        }

        """

        biosample_to_specimen_map = defaultdict(list)

        dataset_sections = find_sections_recursive(
            submission.section, ["Study Component"], []
        )
        for dataset_section in dataset_sections:
            associations = find_sections_recursive(
                dataset_section, ["Associations"], []
            )
            for association in associations:
                association_attributes = attributes_to_dict(association.attributes)

                biosample_reference = association_attributes.get("biosample")
                specimen_reference = association_attributes.get("specimen")

                if isinstance(biosample_reference, str) and isinstance(
                    specimen_reference, str
                ):
                    biosample_to_specimen_map[biosample_reference].append(
                        specimen_reference
                    )

        return biosample_to_specimen_map
