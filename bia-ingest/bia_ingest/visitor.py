"""Implementation of Visitor pattern to traverse submission

Adapted from https://third-bit.com/sdxpy/check/#check-visitor-pattern
"""

import re
import uuid
import hashlib
from typing import List, Dict, Union
from .models import BIAStudy, Publication, Author, Affiliation
from bia_integrator_api.models.biosample import Biosample
from .conversion import generate_biosample_uuid


class Visitor:
    def __init__(self, accession_id: str, create_api_models: bool = False) -> None:
        self.accession_id = accession_id
        self.indent_level = 0
        self.result = {"study": [{},]}
        self.current_result_key = "study"
        self.common_name_matcher = re.compile(r"\((.*)\)")
        self.flattened_contents = []
        self.flattened_contents_dict = {}
        self.create_api_models = create_api_models
        # self.study = BIAStudy()

    def visit(self, parent: str, node: Union[str, List, Dict]) -> None:
        if isinstance(node, str):
            self._text(parent, node)
        elif isinstance(node, list):
            self._tag_enter(parent, node)
            for i, n in enumerate(node):
                self.visit(f"{parent}[{i}]", n)
            self._tag_exit(parent, node)
        elif isinstance(node, dict):
            if "type" in node:
                parent += f".{node['type']}".replace(" ", "_")
            self._tag_enter(parent, node)
            for child in node:
                self.visit(f"{parent}.{child}", node[child])
            self._tag_exit(parent, node)

    def reset(self, accession_id: str, create_api_models: bool = False) -> None:
        self.__init__(accession_id, create_api_models)

    def _tag_enter(self, parent: str, node: Union[List, Dict]) -> None:
        if isinstance(node, list):
            pass
            # print(f"{self.indent_level * '  '}Entering node '{parent}'. List with {len(node)} elements")
        elif isinstance(node, dict):
            if "type" in node:
                node_type = node["type"].lower().replace(" ", "_")
                print(
                    f"{self.indent_level * '  '}Entering node '{parent}'. Dict of type: {node['type']}"
                )
                if node_type == "submission" or node_type == "study":
                    node_type = "study"
                    if node_type not in self.result:
                        self.result["study"] = [
                            {},
                        ]
                elif node_type not in self.result:
                    self.result[node_type] = [
                        {},
                    ]
                else:
                    self.result[node_type].append({})

                self.current_result_key = node_type

            # print(f"{self.indent_level * '  '}Entering node '{parent}'. Dict with keys: {', '.join(node.keys())}")
        self.indent_level += 1

    def _tag_exit(self, parent: str, node: Union[List, Dict]) -> None:
        self.indent_level -= 1
        if isinstance(node, list):
            pass
            # print(f"{self.indent_level * '  '}Exiting node '{parent}'. List with {len(node)} elements")
        elif isinstance(node, dict):
            if "type" in node:
                node_type = node["type"].lower()
                print(
                    f"{self.indent_level * '  '}Exiting node '{parent}'. Dict of type: {node['type']}"
                )
                # print(f"{self.indent_level * '  '}Exiting node '{parent}'. Dict with keys: {', '.join(node.keys())}")

                # Create Biosample
                if node_type == "biosample" and self.create_api_models:
                    biosample_dict = {}
                    for key, value in self.result[node_type][-1].items():
                        if key.endswith("variable"):
                            continue
                        if type(value) is list:
                            biosample_dict[key] = " ".join(value)
                        else:
                            biosample_dict[key] = value
                    try:
                        organism_scientific_name, organism_common_name = biosample_dict[
                            "organism"
                        ].split("(")
                        organism_common_name = organism_common_name.rstrip(")")
                    except ValueError:
                        organism_scientific_name = biosample_dict["organism"]
                        organism_common_name = ""
                    biosample_dict[
                        "organism_scientific_name"
                    ] = organism_scientific_name.strip()
                    biosample_dict[
                        "organism_common_name"
                    ] = organism_common_name.strip()
                    biosample_dict["organism_ncbi_taxon"] = ""
                    biosample_dict["version"] = 0
                    biosample_dict["accession_id"] = self.accession_id

                    for key in ["intrinsic", "extrinsic", "experimental"]:
                        key2 = f"{key}_variable"
                        if key2 in self.result[node_type][-1]:
                            biosample_dict[f"{key2}s"] = self.result[node_type][-1][
                                key2
                            ]

                    print(f"biosample_dict = {biosample_dict}")
                    biosample_dict["uuid"] = generate_biosample_uuid(biosample_dict)
                    biosample = Biosample(**biosample_dict)
                    self.extracted_entities = {
                        node_type: [biosample],
                    }

    def _text(self, parent: str, node: str) -> None:
        indent = (self.indent_level + 1) * "  "
        print(f"{indent}In node '{parent}' with string value: {node}")
        self.flattened_contents.append({parent: node})
        self.flattened_contents_dict.update({parent: node})
        node_key = node.lower().replace(" ", "_")
        if self._is_attribute_name(parent):
            if node_key not in self.result[self.current_result_key][-1]:
                # Use list to store values of attributes as some
                # attribute names are repeated - e.g. 'Keywords'
                self.result[self.current_result_key][-1][node_key] = []
            self.last_attribute_key = node_key
        elif self._is_attribute_value(parent):
            self.result[self.current_result_key][-1][self.last_attribute_key].append(
                node
            )
        elif self._is_value_qualifier_name(parent):
            # Remember value qualifier name and use as key when processing value
            self._current_value_qualifier_name = node
        elif self._is_value_qualifier_value(parent):
            self.result[self.current_result_key][-1][self.last_attribute_key].append(
                {self._current_value_qualifier_name: node}
            )
            self._current_value_qualifier_name = None
        else:
            key = parent.split(".")[-1]
            self.result[self.current_result_key][-1][key] = node

    def _is_attribute_name(self, node_ref: str) -> bool:
        """Check if a node reference is an attribute name"""

        return len(re.findall(r"attributes\[[0-9]{1,3}]\.name", node_ref)) > 0

    def _is_attribute_value(self, node_ref: str) -> bool:
        """Check if a node reference is an attribute value"""

        return len(re.findall(r"attributes\[[0-9]{1,3}]\.value", node_ref)) > 0

    def _is_value_qualifier_name(self, node_ref: str) -> bool:
        """Check if a node reference is a value qualifier name"""

        return len(re.findall(r"valqual\[[0-9]{1,3}]\.name", node_ref)) > 0

    def _is_value_qualifier_value(self, node_ref: str) -> bool:
        """Check if a node reference is a value qualifier value"""

        return len(re.findall(r"valqual\[[0-9]{1,3}]\.value", node_ref)) > 0

    def _dict_to_uuid(self, my_dict: Dict, attributes_to_consider: List[str]) -> str:
        """Create uuid from specific keys in a dictionary

        """

        seed = "".join([my_dict[attr] for attr in attributes_to_consider]).strip()
        hexdigest = hashlib.md5(seed.encode("utf-8")).hexdigest()
        return str(uuid.UUID(version=4, hex=hexdigest))
