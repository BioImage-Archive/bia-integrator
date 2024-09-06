from bia_integrator_api.util import get_client_private
from bia_integrator_api.exceptions import NotFoundException, ApiException
import bia_integrator_api.models as api_models
import inspect
import glob
import json

api_base_url = "https://wwwdev.ebi.ac.uk/bioimage-archive/api"
client = get_client_private(
    username="test@example.com",
    password="test",
    api_base_url=api_base_url
)

for file_name in glob.glob("../../../bia-export/test/input_data/**/*.json", recursive=True):
    # Instead of sorting dependencies, rerun until everything is created
    print(file_name)
    with open(file_name) as f:
        data = json.load(f)
        if 'model' not in data:
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
                raise Exception(file_name, candidates)
        else:
            data_parsed = getattr(api_models, data['model']['type_name'])(**data)
        
        data_parsed.version = 0 # version starts at 0
        
        print(file_name)
        try:
            if data_parsed.model.type_name == "Study":
                client.post_study(data_parsed)
            elif data_parsed.model.type_name == "ImageAnnotationDataset":
                client.post_image_annotation_dataset(data_parsed)
            elif data_parsed.model.type_name == "ExperimentalImagingDataset":
                client.post_experimental_imaging_dataset(data_parsed)
            elif data_parsed.model.type_name == "AnnotationMethod":
                client.post_annotation_method(data_parsed)
            elif data_parsed.model.type_name == "FileReference":
                client.post_file_reference(data_parsed)
            elif data_parsed.model.type_name == "Specimen":
                client.post_specimen(data_parsed)
            elif data_parsed.model.type_name == "ImageRepresentation":
                client.post_image_representation(data_parsed)
            elif data_parsed.model.type_name == "DerivedImage":
                client.post_derived_image(data_parsed)
            elif data_parsed.model.type_name == "ExperimentallyCapturedImage":
                client.post_experimentally_captured_image(data_parsed)
            elif data_parsed.model.type_name == "SpecimenGrowthProtocol":
                client.post_specimen_growth_protocol(data_parsed)
            elif data_parsed.model.type_name == "BioSample":
                client.post_bio_sample(data_parsed)
            elif data_parsed.model.type_name == "ImageAcquisition":
                client.post_image_acquisition(data_parsed)
            elif data_parsed.model.type_name == "SpecimenImagingPreparationProtocol":
                client.post_specimen_imaging_preparation_protocol(data_parsed)
            else:
                raise Exception(data_parsed)
        except NotFoundException as e:
            print(e)
        except ApiException as e:
            print(e)


