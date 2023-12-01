from bia_integrator_api.util import simple_client, PrivateApi
import bia_integrator_api.models as api_models
from src.bia_integrator_core import interface
from typing import Union

import json
import os
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(SCRIPT_DIR, "config.json"), "r") as f:
    config = json.load(f)["dev"]

from subprocess import check_output

report = {}

def find_string_in_submission_history(subm_accno, str_to_search):
    data_repo_path = os.path.expanduser("~/.bia-integrator-data")
    submission_path = check_output(f"find ./studies -name *{subm_accno}*".split(" "), cwd=data_repo_path).decode().strip()
    needle_occ = check_output(f"git log -p -- {submission_path} | grep \\\"{str_to_search}\\\"", cwd=data_repo_path, shell=True).decode().strip().split("\n")
    
    return needle_occ

# @TODO: handle FileReference, ImageRepresentation separately - they have attributes but don't have annotations
def doc_categorise_annotations(doc: Union[api_models.BIAStudy, api_models.BIAImage]):
    def doc_get_description(doc: Union[api_models.BIAStudy, api_models.BIAImage]):
        if type(doc) is api_models.BIAStudy:
            return f"Study {doc.uuid}, accession {doc.accession_id}"
        elif type(doc) is api_models.BIAImage:
            return f"Image {doc.uuid}, parent study {doc.study_uuid}, alias {doc.alias and doc.alias.name}"

    if not doc.annotations:
        doc.annotations = []
    if not doc.attributes:
        doc.attributes = {}
    
    doc_annotations_possibly_applied = {
        "overwrite_attributes": [],
        "overwrite_fields": []
    }
    for annotation in doc.annotations:
        if annotation.key in doc.attributes and annotation.value == doc.attributes[annotation.key]:
            mismatched_old_value = []
            for occ in find_string_in_submission_history(doc.accession_id, annotation.key):
                log_item_as_json = "{" + occ[1:].rstrip(",") + "}"
                if json.loads(log_item_as_json)[annotation.key] != annotation.value:
                    mismatched_old_value.append(occ)

            if mismatched_old_value:
                # ! At some point in time, the submission had a different value in this attribute
                doc_annotations_possibly_applied["overwrite_attributes"].append({
                    "annotation": annotation.key,
                    "old_values": find_string_in_submission_history(doc.accession_id, annotation.key),
                    "annotation_value": annotation.value
                })
        elif annotation.key in doc.dict() and doc.dict()[annotation.key] == annotation.value:
            known_to_overwrite_doc_attributes = ["example_image_uri", "imaging_type", "organism"]
            if annotation.key in known_to_overwrite_doc_attributes:
                mismatched_old_value = []
                for occ in find_string_in_submission_history(doc.accession_id, annotation.key):
                    log_item_as_json = "{" + occ[1:].rstrip(",") + "}"
                    if json.loads(log_item_as_json)[annotation.key] != annotation.value:
                        mismatched_old_value.append(occ)

                if mismatched_old_value:
                    doc_annotations_possibly_applied["overwrite_fields"].append({
                        "annotation": annotation.key,
                        "old_values": mismatched_old_value,
                        "annotation_value": annotation.value
                    })
            else:
                print(annotation.key)
                raise Exception(f"Only annotations that overwrite the following attributes {known_to_overwrite_doc_attributes} known of. Found {annotation.key}")

    #annotation_keys = set([annotation.key for annotation in doc.annotations])
    #attribute_keys = set(doc.attributes.keys())

    #attributes_not_annotations = attribute_keys.difference(annotation_keys)
    #if attributes_not_annotations:
    #    print(doc_get_description(doc))
    #    print(attributes_not_annotations)
    #assert attribute_keys.intersection(annotation_keys) == attribute_keys

    #k_annotations_possibly_applied = doc_annotations_possibly_applied
    #k_annotations_possibly_applied = ",".join(sorted(doc_annotations_possibly_applied))
    if doc_annotations_possibly_applied["overwrite_attributes"] or doc_annotations_possibly_applied["overwrite_fields"]:
        if type(doc) is api_models.BIAStudy:
            #print(f"Study {doc.uuid}, accession {doc.accession_id}")
            report[doc.uuid] = report.get(doc.uuid, {})
            report[doc.uuid]['study_overwritten'] = doc_annotations_possibly_applied
            report[doc.uuid]['accession_id'] = doc.accession_id
        elif type(doc) is api_models.BIAImage:
            raise Exception("No images expected to have had annotations applied")
            report[doc.study_uuid] = report.get(doc.study_uuid, {})
            report[doc.study_uuid]['images_overwritten_by_mode'] = report[doc.study_uuid].get("images_overwritten_by_mode", {})
            report[doc.study_uuid]['images_overwritten_by_mode'][k_annotations_possibly_applied] = report[doc.study_uuid]['images_overwritten_by_mode'].get(k_annotations_possibly_applied, [])
            report[doc.study_uuid]['images_overwritten_by_mode'][k_annotations_possibly_applied].append(doc.uuid)

            #print(f"Image {doc.uuid}, parent study {doc.study_uuid}, alias {doc.alias and doc.alias.name}")
        #print(annotations_not_in_attributes)
        #print("")
    
    #for annotation in doc.annotations:
    #    if annotation.key in doc.attributes:
    #        # check that all annotations are already applied
            #assert doc.attributes[annotation.key] == annotation.value

def assert_annotations_not_in_attributes(api_client: PrivateApi):
    """
    Check using only api data just for the sake of using a different method
    """

    for api_study in api_client.search_studies(limit=1000000):
        doc_categorise_annotations(api_study)

        for api_image in api_client.get_study_images(api_study.uuid, limit=1000000000):
            doc_categorise_annotations(api_image)

if __name__ == "__main__":
    api_client = simple_client(
        config["biaint_api_url"],
        config["biaint_username"],
        config["biaint_password"],
        disable_ssl_host_check = True
    )

    assert_annotations_not_in_attributes(api_client)

    print(json.dumps(report, indent=4))
    #occ = find_string_in_submission_history("S-BIAD608", "example_image_uri")
    #print(occ)