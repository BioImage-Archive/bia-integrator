# bia_integrator_api.PrivateApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_annotation_data**](PrivateApi.md#get_annotation_data) | **GET** /v2/annotation_data/{uuid} | Get AnnotationData
[**get_annotation_data_linking_creation_process**](PrivateApi.md#get_annotation_data_linking_creation_process) | **GET** /v2/creation_process/{uuid}/annotation_data | Get AnnotationData Linking CreationProcess
[**get_annotation_data_linking_dataset**](PrivateApi.md#get_annotation_data_linking_dataset) | **GET** /v2/dataset/{uuid}/annotation_data | Get AnnotationData Linking Dataset
[**get_annotation_data_linking_file_reference**](PrivateApi.md#get_annotation_data_linking_file_reference) | **GET** /v2/file_reference/{uuid}/annotation_data | Get AnnotationData Linking FileReference
[**get_annotation_method**](PrivateApi.md#get_annotation_method) | **GET** /v2/annotation_method/{uuid} | Get AnnotationMethod
[**get_bio_sample**](PrivateApi.md#get_bio_sample) | **GET** /v2/bio_sample/{uuid} | Get BioSample
[**get_bio_sample_linking_protocol**](PrivateApi.md#get_bio_sample_linking_protocol) | **GET** /v2/protocol/{uuid}/bio_sample | Get BioSample Linking Protocol
[**get_creation_process**](PrivateApi.md#get_creation_process) | **GET** /v2/creation_process/{uuid} | Get CreationProcess
[**get_creation_process_linking_annotation_method**](PrivateApi.md#get_creation_process_linking_annotation_method) | **GET** /v2/annotation_method/{uuid}/creation_process | Get CreationProcess Linking AnnotationMethod
[**get_creation_process_linking_image**](PrivateApi.md#get_creation_process_linking_image) | **GET** /v2/image/{uuid}/creation_process | Get CreationProcess Linking Image
[**get_creation_process_linking_image_acquisition_protocol**](PrivateApi.md#get_creation_process_linking_image_acquisition_protocol) | **GET** /v2/image_acquisition_protocol/{uuid}/creation_process | Get CreationProcess Linking ImageAcquisitionProtocol
[**get_creation_process_linking_protocol**](PrivateApi.md#get_creation_process_linking_protocol) | **GET** /v2/protocol/{uuid}/creation_process | Get CreationProcess Linking Protocol
[**get_creation_process_linking_specimen**](PrivateApi.md#get_creation_process_linking_specimen) | **GET** /v2/specimen/{uuid}/creation_process | Get CreationProcess Linking Specimen
[**get_dataset**](PrivateApi.md#get_dataset) | **GET** /v2/dataset/{uuid} | Get Dataset
[**get_dataset_linking_study**](PrivateApi.md#get_dataset_linking_study) | **GET** /v2/study/{uuid}/dataset | Get Dataset Linking Study
[**get_file_reference**](PrivateApi.md#get_file_reference) | **GET** /v2/file_reference/{uuid} | Get FileReference
[**get_file_reference_linking_dataset**](PrivateApi.md#get_file_reference_linking_dataset) | **GET** /v2/dataset/{uuid}/file_reference | Get FileReference Linking Dataset
[**get_image**](PrivateApi.md#get_image) | **GET** /v2/image/{uuid} | Get Image
[**get_image_acquisition_protocol**](PrivateApi.md#get_image_acquisition_protocol) | **GET** /v2/image_acquisition_protocol/{uuid} | Get ImageAcquisitionProtocol
[**get_image_linking_creation_process**](PrivateApi.md#get_image_linking_creation_process) | **GET** /v2/creation_process/{uuid}/image | Get Image Linking CreationProcess
[**get_image_linking_dataset**](PrivateApi.md#get_image_linking_dataset) | **GET** /v2/dataset/{uuid}/image | Get Image Linking Dataset
[**get_image_linking_file_reference**](PrivateApi.md#get_image_linking_file_reference) | **GET** /v2/file_reference/{uuid}/image | Get Image Linking FileReference
[**get_image_representation**](PrivateApi.md#get_image_representation) | **GET** /v2/image_representation/{uuid} | Get ImageRepresentation
[**get_image_representation_linking_image**](PrivateApi.md#get_image_representation_linking_image) | **GET** /v2/image/{uuid}/image_representation | Get ImageRepresentation Linking Image
[**get_protocol**](PrivateApi.md#get_protocol) | **GET** /v2/protocol/{uuid} | Get Protocol
[**get_specimen**](PrivateApi.md#get_specimen) | **GET** /v2/specimen/{uuid} | Get Specimen
[**get_specimen_imaging_preparation_protocol**](PrivateApi.md#get_specimen_imaging_preparation_protocol) | **GET** /v2/specimen_imaging_preparation_protocol/{uuid} | Get SpecimenImagingPreparationProtocol
[**get_specimen_linking_bio_sample**](PrivateApi.md#get_specimen_linking_bio_sample) | **GET** /v2/bio_sample/{uuid}/specimen | Get Specimen Linking BioSample
[**get_specimen_linking_specimen_imaging_preparation_protocol**](PrivateApi.md#get_specimen_linking_specimen_imaging_preparation_protocol) | **GET** /v2/specimen_imaging_preparation_protocol/{uuid}/specimen | Get Specimen Linking SpecimenImagingPreparationProtocol
[**get_studies**](PrivateApi.md#get_studies) | **GET** /v2/study | Getstudies
[**get_study**](PrivateApi.md#get_study) | **GET** /v2/study/{uuid} | Get Study
[**login_for_access_token**](PrivateApi.md#login_for_access_token) | **POST** /v2/auth/token | Login For Access Token
[**post_annotation_data**](PrivateApi.md#post_annotation_data) | **POST** /v2/private/annotation_data | Create AnnotationData
[**post_annotation_method**](PrivateApi.md#post_annotation_method) | **POST** /v2/private/annotation_method | Create AnnotationMethod
[**post_bio_sample**](PrivateApi.md#post_bio_sample) | **POST** /v2/private/bio_sample | Create BioSample
[**post_creation_process**](PrivateApi.md#post_creation_process) | **POST** /v2/private/creation_process | Create CreationProcess
[**post_dataset**](PrivateApi.md#post_dataset) | **POST** /v2/private/dataset | Create Dataset
[**post_file_reference**](PrivateApi.md#post_file_reference) | **POST** /v2/private/file_reference | Create FileReference
[**post_image**](PrivateApi.md#post_image) | **POST** /v2/private/image | Create Image
[**post_image_acquisition_protocol**](PrivateApi.md#post_image_acquisition_protocol) | **POST** /v2/private/image_acquisition_protocol | Create ImageAcquisitionProtocol
[**post_image_representation**](PrivateApi.md#post_image_representation) | **POST** /v2/private/image_representation | Create ImageRepresentation
[**post_protocol**](PrivateApi.md#post_protocol) | **POST** /v2/private/protocol | Create Protocol
[**post_specimen**](PrivateApi.md#post_specimen) | **POST** /v2/private/specimen | Create Specimen
[**post_specimen_imaging_preparation_protocol**](PrivateApi.md#post_specimen_imaging_preparation_protocol) | **POST** /v2/private/specimen_imaging_preparation_protocol | Create SpecimenImagingPreparationProtocol
[**post_study**](PrivateApi.md#post_study) | **POST** /v2/private/study | Create Study
[**register_user**](PrivateApi.md#register_user) | **POST** /v2/auth/user/register | Register User
[**search_image_representation_by_file_uri**](PrivateApi.md#search_image_representation_by_file_uri) | **GET** /v2/search/image_representation/file_uri_fragment | Searchimagerepresentationbyfileuri
[**search_study_by_accession**](PrivateApi.md#search_study_by_accession) | **GET** /v2/search/study/accession | Searchstudybyaccession


# **get_annotation_data**
> AnnotationData get_annotation_data(uuid)

Get AnnotationData

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_data import AnnotationData
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get AnnotationData
        api_response = api_instance.get_annotation_data(uuid)
        print("The response of PrivateApi->get_annotation_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_annotation_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**AnnotationData**](AnnotationData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_annotation_data_linking_creation_process**
> List[AnnotationData] get_annotation_data_linking_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)

Get AnnotationData Linking CreationProcess

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_data import AnnotationData
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get AnnotationData Linking CreationProcess
        api_response = api_instance.get_annotation_data_linking_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_annotation_data_linking_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_annotation_data_linking_creation_process: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationData]**](AnnotationData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_annotation_data_linking_dataset**
> List[AnnotationData] get_annotation_data_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)

Get AnnotationData Linking Dataset

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_data import AnnotationData
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get AnnotationData Linking Dataset
        api_response = api_instance.get_annotation_data_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_annotation_data_linking_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_annotation_data_linking_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationData]**](AnnotationData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_annotation_data_linking_file_reference**
> List[AnnotationData] get_annotation_data_linking_file_reference(uuid, page_size, start_from_uuid=start_from_uuid)

Get AnnotationData Linking FileReference

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_data import AnnotationData
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get AnnotationData Linking FileReference
        api_response = api_instance.get_annotation_data_linking_file_reference(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_annotation_data_linking_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_annotation_data_linking_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationData]**](AnnotationData.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_annotation_method**
> AnnotationMethod get_annotation_method(uuid)

Get AnnotationMethod

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_method import AnnotationMethod
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get AnnotationMethod
        api_response = api_instance.get_annotation_method(uuid)
        print("The response of PrivateApi->get_annotation_method:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_annotation_method: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**AnnotationMethod**](AnnotationMethod.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bio_sample**
> BioSample get_bio_sample(uuid)

Get BioSample

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.bio_sample import BioSample
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get BioSample
        api_response = api_instance.get_bio_sample(uuid)
        print("The response of PrivateApi->get_bio_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_bio_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**BioSample**](BioSample.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_bio_sample_linking_protocol**
> List[BioSample] get_bio_sample_linking_protocol(uuid, page_size, start_from_uuid=start_from_uuid)

Get BioSample Linking Protocol

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.bio_sample import BioSample
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get BioSample Linking Protocol
        api_response = api_instance.get_bio_sample_linking_protocol(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_bio_sample_linking_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_bio_sample_linking_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[BioSample]**](BioSample.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process**
> CreationProcess get_creation_process(uuid)

Get CreationProcess

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get CreationProcess
        api_response = api_instance.get_creation_process(uuid)
        print("The response of PrivateApi->get_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_creation_process: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**CreationProcess**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process_linking_annotation_method**
> List[CreationProcess] get_creation_process_linking_annotation_method(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess Linking AnnotationMethod

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get CreationProcess Linking AnnotationMethod
        api_response = api_instance.get_creation_process_linking_annotation_method(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_creation_process_linking_annotation_method:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_creation_process_linking_annotation_method: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process_linking_image**
> List[CreationProcess] get_creation_process_linking_image(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess Linking Image

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get CreationProcess Linking Image
        api_response = api_instance.get_creation_process_linking_image(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_creation_process_linking_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_creation_process_linking_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process_linking_image_acquisition_protocol**
> List[CreationProcess] get_creation_process_linking_image_acquisition_protocol(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess Linking ImageAcquisitionProtocol

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get CreationProcess Linking ImageAcquisitionProtocol
        api_response = api_instance.get_creation_process_linking_image_acquisition_protocol(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_creation_process_linking_image_acquisition_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_creation_process_linking_image_acquisition_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process_linking_protocol**
> List[CreationProcess] get_creation_process_linking_protocol(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess Linking Protocol

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get CreationProcess Linking Protocol
        api_response = api_instance.get_creation_process_linking_protocol(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_creation_process_linking_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_creation_process_linking_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_creation_process_linking_specimen**
> List[CreationProcess] get_creation_process_linking_specimen(uuid, page_size, start_from_uuid=start_from_uuid)

Get CreationProcess Linking Specimen

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get CreationProcess Linking Specimen
        api_response = api_instance.get_creation_process_linking_specimen(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_creation_process_linking_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_creation_process_linking_specimen: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[CreationProcess]**](CreationProcess.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_dataset**
> Dataset get_dataset(uuid)

Get Dataset

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.dataset import Dataset
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Dataset
        api_response = api_instance.get_dataset(uuid)
        print("The response of PrivateApi->get_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Dataset**](Dataset.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_dataset_linking_study**
> List[Dataset] get_dataset_linking_study(uuid, page_size, start_from_uuid=start_from_uuid)

Get Dataset Linking Study

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.dataset import Dataset
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Dataset Linking Study
        api_response = api_instance.get_dataset_linking_study(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_dataset_linking_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_dataset_linking_study: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Dataset]**](Dataset.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_file_reference**
> FileReference get_file_reference(uuid)

Get FileReference

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.file_reference import FileReference
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get FileReference
        api_response = api_instance.get_file_reference(uuid)
        print("The response of PrivateApi->get_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**FileReference**](FileReference.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_file_reference_linking_dataset**
> List[FileReference] get_file_reference_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)

Get FileReference Linking Dataset

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.file_reference import FileReference
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get FileReference Linking Dataset
        api_response = api_instance.get_file_reference_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_file_reference_linking_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_file_reference_linking_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[FileReference]**](FileReference.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image**
> Image get_image(uuid)

Get Image

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image import Image
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Image
        api_response = api_instance.get_image(uuid)
        print("The response of PrivateApi->get_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Image**](Image.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_acquisition_protocol**
> ImageAcquisitionProtocol get_image_acquisition_protocol(uuid)

Get ImageAcquisitionProtocol

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_acquisition_protocol import ImageAcquisitionProtocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get ImageAcquisitionProtocol
        api_response = api_instance.get_image_acquisition_protocol(uuid)
        print("The response of PrivateApi->get_image_acquisition_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_image_acquisition_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**ImageAcquisitionProtocol**](ImageAcquisitionProtocol.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_linking_creation_process**
> List[Image] get_image_linking_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)

Get Image Linking CreationProcess

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image import Image
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Image Linking CreationProcess
        api_response = api_instance.get_image_linking_creation_process(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_image_linking_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_image_linking_creation_process: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Image]**](Image.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_linking_dataset**
> List[Image] get_image_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)

Get Image Linking Dataset

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image import Image
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Image Linking Dataset
        api_response = api_instance.get_image_linking_dataset(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_image_linking_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_image_linking_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Image]**](Image.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_linking_file_reference**
> List[Image] get_image_linking_file_reference(uuid, page_size, start_from_uuid=start_from_uuid)

Get Image Linking FileReference

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image import Image
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Image Linking FileReference
        api_response = api_instance.get_image_linking_file_reference(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_image_linking_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_image_linking_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Image]**](Image.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_representation**
> ImageRepresentation get_image_representation(uuid)

Get ImageRepresentation

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_representation import ImageRepresentation
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get ImageRepresentation
        api_response = api_instance.get_image_representation(uuid)
        print("The response of PrivateApi->get_image_representation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_image_representation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**ImageRepresentation**](ImageRepresentation.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_image_representation_linking_image**
> List[ImageRepresentation] get_image_representation_linking_image(uuid, page_size, start_from_uuid=start_from_uuid)

Get ImageRepresentation Linking Image

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_representation import ImageRepresentation
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get ImageRepresentation Linking Image
        api_response = api_instance.get_image_representation_linking_image(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_image_representation_linking_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_image_representation_linking_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[ImageRepresentation]**](ImageRepresentation.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_protocol**
> Protocol get_protocol(uuid)

Get Protocol

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.protocol import Protocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Protocol
        api_response = api_instance.get_protocol(uuid)
        print("The response of PrivateApi->get_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Protocol**](Protocol.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_specimen**
> Specimen get_specimen(uuid)

Get Specimen

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Specimen
        api_response = api_instance.get_specimen(uuid)
        print("The response of PrivateApi->get_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_specimen: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Specimen**](Specimen.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_specimen_imaging_preparation_protocol**
> SpecimenImagingPreparationProtocol get_specimen_imaging_preparation_protocol(uuid)

Get SpecimenImagingPreparationProtocol

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen_imaging_preparation_protocol import SpecimenImagingPreparationProtocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get SpecimenImagingPreparationProtocol
        api_response = api_instance.get_specimen_imaging_preparation_protocol(uuid)
        print("The response of PrivateApi->get_specimen_imaging_preparation_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_specimen_imaging_preparation_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**SpecimenImagingPreparationProtocol**](SpecimenImagingPreparationProtocol.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_specimen_linking_bio_sample**
> List[Specimen] get_specimen_linking_bio_sample(uuid, page_size, start_from_uuid=start_from_uuid)

Get Specimen Linking BioSample

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Specimen Linking BioSample
        api_response = api_instance.get_specimen_linking_bio_sample(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_specimen_linking_bio_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_specimen_linking_bio_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Specimen]**](Specimen.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_specimen_linking_specimen_imaging_preparation_protocol**
> List[Specimen] get_specimen_linking_specimen_imaging_preparation_protocol(uuid, page_size, start_from_uuid=start_from_uuid)

Get Specimen Linking SpecimenImagingPreparationProtocol

Naming convention is getSourceLinkingTarget, where source/target refer to the start/end of the linking arrow in the model diagram

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Get Specimen Linking SpecimenImagingPreparationProtocol
        api_response = api_instance.get_specimen_linking_specimen_imaging_preparation_protocol(uuid, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_specimen_linking_specimen_imaging_preparation_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_specimen_linking_specimen_imaging_preparation_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Specimen]**](Specimen.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_studies**
> List[Study] get_studies(page_size, start_from_uuid=start_from_uuid)

Getstudies

@TODO: Filters?  @TODO: Not pluralizing clashes with getStudy(study_uuid) - non-pluralised convention?

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.study import Study
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Getstudies
        api_response = api_instance.get_studies(page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->get_studies:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_studies: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[Study]**](Study.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_study**
> Study get_study(uuid)

Get Study

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.study import Study
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Study
        api_response = api_instance.get_study(uuid)
        print("The response of PrivateApi->get_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_study: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**Study**](Study.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **login_for_access_token**
> AuthenticationToken login_for_access_token(username, password, grant_type=grant_type, scope=scope, client_id=client_id, client_secret=client_secret)

Login For Access Token

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.authentication_token import AuthenticationToken
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    username = 'username_example' # str | 
    password = 'password_example' # str | 
    grant_type = 'grant_type_example' # str |  (optional)
    scope = '' # str |  (optional) (default to '')
    client_id = 'client_id_example' # str |  (optional)
    client_secret = 'client_secret_example' # str |  (optional)

    try:
        # Login For Access Token
        api_response = api_instance.login_for_access_token(username, password, grant_type=grant_type, scope=scope, client_id=client_id, client_secret=client_secret)
        print("The response of PrivateApi->login_for_access_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->login_for_access_token: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **username** | **str**|  | 
 **password** | **str**|  | 
 **grant_type** | **str**|  | [optional] 
 **scope** | **str**|  | [optional] [default to &#39;&#39;]
 **client_id** | **str**|  | [optional] 
 **client_secret** | **str**|  | [optional] 

### Return type

[**AuthenticationToken**](AuthenticationToken.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_annotation_data**
> object post_annotation_data(annotation_data)

Create AnnotationData

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.annotation_data import AnnotationData
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    annotation_data = bia_integrator_api.AnnotationData() # AnnotationData | 

    try:
        # Create AnnotationData
        api_response = api_instance.post_annotation_data(annotation_data)
        print("The response of PrivateApi->post_annotation_data:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_annotation_data: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **annotation_data** | [**AnnotationData**](AnnotationData.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_annotation_method**
> object post_annotation_method(annotation_method)

Create AnnotationMethod

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.annotation_method import AnnotationMethod
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    annotation_method = bia_integrator_api.AnnotationMethod() # AnnotationMethod | 

    try:
        # Create AnnotationMethod
        api_response = api_instance.post_annotation_method(annotation_method)
        print("The response of PrivateApi->post_annotation_method:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_annotation_method: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **annotation_method** | [**AnnotationMethod**](AnnotationMethod.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_bio_sample**
> object post_bio_sample(bio_sample)

Create BioSample

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.bio_sample import BioSample
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    bio_sample = bia_integrator_api.BioSample() # BioSample | 

    try:
        # Create BioSample
        api_response = api_instance.post_bio_sample(bio_sample)
        print("The response of PrivateApi->post_bio_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_bio_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bio_sample** | [**BioSample**](BioSample.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_creation_process**
> object post_creation_process(creation_process)

Create CreationProcess

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.creation_process import CreationProcess
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    creation_process = bia_integrator_api.CreationProcess() # CreationProcess | 

    try:
        # Create CreationProcess
        api_response = api_instance.post_creation_process(creation_process)
        print("The response of PrivateApi->post_creation_process:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_creation_process: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **creation_process** | [**CreationProcess**](CreationProcess.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_dataset**
> object post_dataset(dataset)

Create Dataset

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.dataset import Dataset
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    dataset = bia_integrator_api.Dataset() # Dataset | 

    try:
        # Create Dataset
        api_response = api_instance.post_dataset(dataset)
        print("The response of PrivateApi->post_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **dataset** | [**Dataset**](Dataset.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_file_reference**
> object post_file_reference(file_reference)

Create FileReference

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.file_reference import FileReference
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    file_reference = bia_integrator_api.FileReference() # FileReference | 

    try:
        # Create FileReference
        api_response = api_instance.post_file_reference(file_reference)
        print("The response of PrivateApi->post_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_reference** | [**FileReference**](FileReference.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_image**
> object post_image(image)

Create Image

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.image import Image
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    image = bia_integrator_api.Image() # Image | 

    try:
        # Create Image
        api_response = api_instance.post_image(image)
        print("The response of PrivateApi->post_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image** | [**Image**](Image.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_image_acquisition_protocol**
> object post_image_acquisition_protocol(image_acquisition_protocol)

Create ImageAcquisitionProtocol

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.image_acquisition_protocol import ImageAcquisitionProtocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    image_acquisition_protocol = bia_integrator_api.ImageAcquisitionProtocol() # ImageAcquisitionProtocol | 

    try:
        # Create ImageAcquisitionProtocol
        api_response = api_instance.post_image_acquisition_protocol(image_acquisition_protocol)
        print("The response of PrivateApi->post_image_acquisition_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_image_acquisition_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_acquisition_protocol** | [**ImageAcquisitionProtocol**](ImageAcquisitionProtocol.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_image_representation**
> object post_image_representation(image_representation)

Create ImageRepresentation

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.image_representation import ImageRepresentation
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    image_representation = bia_integrator_api.ImageRepresentation() # ImageRepresentation | 

    try:
        # Create ImageRepresentation
        api_response = api_instance.post_image_representation(image_representation)
        print("The response of PrivateApi->post_image_representation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_image_representation: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_representation** | [**ImageRepresentation**](ImageRepresentation.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_protocol**
> object post_protocol(protocol)

Create Protocol

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.protocol import Protocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    protocol = bia_integrator_api.Protocol() # Protocol | 

    try:
        # Create Protocol
        api_response = api_instance.post_protocol(protocol)
        print("The response of PrivateApi->post_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **protocol** | [**Protocol**](Protocol.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_specimen**
> object post_specimen(specimen)

Create Specimen

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.specimen import Specimen
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    specimen = bia_integrator_api.Specimen() # Specimen | 

    try:
        # Create Specimen
        api_response = api_instance.post_specimen(specimen)
        print("The response of PrivateApi->post_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_specimen: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **specimen** | [**Specimen**](Specimen.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_specimen_imaging_preparation_protocol**
> object post_specimen_imaging_preparation_protocol(specimen_imaging_preparation_protocol)

Create SpecimenImagingPreparationProtocol

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.specimen_imaging_preparation_protocol import SpecimenImagingPreparationProtocol
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    specimen_imaging_preparation_protocol = bia_integrator_api.SpecimenImagingPreparationProtocol() # SpecimenImagingPreparationProtocol | 

    try:
        # Create SpecimenImagingPreparationProtocol
        api_response = api_instance.post_specimen_imaging_preparation_protocol(specimen_imaging_preparation_protocol)
        print("The response of PrivateApi->post_specimen_imaging_preparation_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_specimen_imaging_preparation_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **specimen_imaging_preparation_protocol** | [**SpecimenImagingPreparationProtocol**](SpecimenImagingPreparationProtocol.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **post_study**
> object post_study(study)

Create Study

### Example

* OAuth Authentication (OAuth2PasswordBearer):

```python
import bia_integrator_api
from bia_integrator_api.models.study import Study
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    study = bia_integrator_api.Study() # Study | 

    try:
        # Create Study
        api_response = api_instance.post_study(study)
        print("The response of PrivateApi->post_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_study: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study** | [**Study**](Study.md)|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **register_user**
> object register_user(body_register_user)

Register User

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.body_register_user import BodyRegisterUser
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    body_register_user = bia_integrator_api.BodyRegisterUser() # BodyRegisterUser | 

    try:
        # Register User
        api_response = api_instance.register_user(body_register_user)
        print("The response of PrivateApi->register_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->register_user: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **body_register_user** | [**BodyRegisterUser**](BodyRegisterUser.md)|  | 

### Return type

**object**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_image_representation_by_file_uri**
> List[ImageRepresentation] search_image_representation_by_file_uri(file_uri, page_size, start_from_uuid=start_from_uuid)

Searchimagerepresentationbyfileuri

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_representation import ImageRepresentation
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    file_uri = 'file_uri_example' # str | 
    page_size = 56 # int | 
    start_from_uuid = 'start_from_uuid_example' # str |  (optional)

    try:
        # Searchimagerepresentationbyfileuri
        api_response = api_instance.search_image_representation_by_file_uri(file_uri, page_size, start_from_uuid=start_from_uuid)
        print("The response of PrivateApi->search_image_representation_by_file_uri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->search_image_representation_by_file_uri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_uri** | **str**|  | 
 **page_size** | **int**|  | 
 **start_from_uuid** | **str**|  | [optional] 

### Return type

[**List[ImageRepresentation]**](ImageRepresentation.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **search_study_by_accession**
> Study search_study_by_accession(accession_id)

Searchstudybyaccession

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.study import Study
from bia_integrator_api.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = bia_integrator_api.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    accession_id = 'accession_id_example' # str | 

    try:
        # Searchstudybyaccession
        api_response = api_instance.search_study_by_accession(accession_id)
        print("The response of PrivateApi->search_study_by_accession:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->search_study_by_accession: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **accession_id** | **str**|  | 

### Return type

[**Study**](Study.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

