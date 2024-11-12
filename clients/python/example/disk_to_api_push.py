from bia_integrator_api.util import get_client_private
from bia_integrator_api.exceptions import NotFoundException, ApiException
from bia_integrator_api import PrivateApi
import bia_integrator_api.models as api_models
import inspect
import json
from pathlib import Path
from multiprocessing import Pool
from enum import Enum
import typer
from typing import Annotated
from functools import partial
import os

"""
Avoid having to pass the api client object as a Process arg, to workaround it not being pickle-able by default
"""
api_client = None


def dict_parse_unknown_model(data: dict, file_name: str):
    if "model" not in data:
        model_classes = [
            model_class
            for name, model_class in inspect.getmembers(api_models)
            if inspect.isclass(model_class)
        ]

        candidates = []
        for model in model_classes:
            try:
                data_parsed = model(**data)
            except Exception:
                pass
            else:
                candidates.append(model)

        if len(candidates) == 1:
            data_parsed = candidates[0](**data)
        else:
            raise Exception(
                "Unable to deserialise into a single model", file_name, candidates
            )
    else:
        data_parsed = getattr(api_models, data["model"]["type_name"])(**data)

    data_parsed.version = 0  # version starts at 0
    return data_parsed


def api_push_json(delete_after_push: bool, json_path: str):
    report = {"already_exists": [], "not_found": []}

    with open(json_path) as f:
        data_parsed = dict_parse_unknown_model(json.load(f), file_name=json_path)

        try:
            if data_parsed.model.type_name == "Study":
                api_client.post_study(data_parsed)
            elif data_parsed.model.type_name == 'FileReference':
                api_client.post_file_reference(data_parsed)
            elif data_parsed.model.type_name == "ImageRepresentation":
                api_client.post_image_representation(data_parsed)
            elif data_parsed.model.type_name == "Dataset":
                api_client.post_dataset(data_parsed)
            elif data_parsed.model.type_name == "Specimen":
                api_client.post_specimen(data_parsed)
            elif data_parsed.model.type_name == "Image":
                api_client.post_image(data_parsed)
            elif data_parsed.model.type_name == "ImageAcquisitionProtocol":
                api_client.post_image_acquisition_protocol(data_parsed)
            elif data_parsed.model.type_name == "SpecimenImagingPreparationProtocol":
                api_client.post_specimen_imaging_preparation_protocol(data_parsed)
            elif data_parsed.model.type_name == "Protocol":
                api_client.post_protocol(data_parsed)
            elif data_parsed.model.type_name == "BioSample":
                api_client.post_bio_sample(data_parsed)
            elif data_parsed.model.type_name == "CreationProcess":
                api_client.post_creation_process(data_parsed)
            elif data_parsed.model.type_name == "AnnotationData":
                api_client.post_annotation_data(data_parsed)
            elif data_parsed.model.type_name == "AnnotationMethod":
                api_client.post_annotation_method(data_parsed)
            else:
                raise Exception(f"Unable to create {data_parsed.model.type_name} {data_parsed.model.type_name == 'FileReference'}", json_path, data_parsed)

            if delete_after_push:
                os.remove(json_path)

        except NotFoundException as e:
            report["not_found"].append(str(json_path))
        except ApiException as e:
            if e.status == 409:
                report["already_exists"].append(str(json_path))

                if delete_after_push:
                    os.remove(json_path)
            else:
                raise

    return report


class ReportModes(Enum):
    REPORT_SUM = "sum"
    REPORT_LIST = "list"


app = typer.Typer()


def make_client(api_base_url, api_username, api_password):
    global api_client
    api_client = get_client_private(
        username=api_username, password=api_password, api_base_url=api_base_url
    )


@app.command(help="Move jsons on disk to the api")
def json_import(
    data_root: Annotated[Path, typer.Argument()],
    report_mode: ReportModes = ReportModes.REPORT_LIST.value,
    threads: int = 1,
    api_base_url: str = "http://localhost:8080",
    api_username: str = "test@example.com",
    api_password: str = "test",
    limit: int = 0,
    warning_this_deletes_source_data_delete_after_push: bool = False,
):
    def glob_key_order(file_abspath):
        # dependency order in https://docs.google.com/drawings/d/1y_0GjhIxhB1hVvjIBoTyEv8_SE1jXuJ_9-QK6ScouBg/edit
        #   to avoid having to rerun
        # or only rerun for cyclical dependencies (if any)
        sort_order = [
            'study',
            'dataset',
            'file_reference',
            'specimen_imaging_preparation_protocol',
            'bio_sample',
            'image_acquisition_protocol'
        ]
        for idx, file_type in enumerate(sort_order):
            if file_type in str(file_abspath):
                return idx

        return len(sort_order) + 1

    jsons_to_push = [str(json_path) for json_path in sorted(data_root.glob("**/*.json"), key=glob_key_order)]
    if limit:
        jsons_to_push = jsons_to_push[:limit]

    if len(jsons_to_push) > 10000 and report_mode == ReportModes.REPORT_LIST.value:
        raise Exception(
            f"Report must be {ReportModes.REPORT_SUM.value}, not {ReportModes.REPORT_LIST.value}"
        )

    #make_client(api_base_url, api_username, api_password)
    #for json in jsons_to_push:
    #    api_push_json(warning_this_deletes_source_data_delete_after_push, json)
    #return

    with Pool(
        processes=threads,
        initializer=make_client,
        initargs=(api_base_url, api_username, api_password),
    ) as p:
        report = {}
        for report_job in p.map(
            partial(api_push_json, warning_this_deletes_source_data_delete_after_push),
            jsons_to_push,
            chunksize=1000 # smaller chunks mean sorted jsons at the start get pushed first -> fewer reruns 
        ):
            for k, v in report_job.items():
                if report_mode is ReportModes.REPORT_SUM:
                    report[k] = report.get(k, 0) + len(v)
                else:
                    report[k] = report.get(k, []) + v

    print(json.dumps(report, sort_keys=True, indent=4))


if __name__ == "__main__":
    app()
