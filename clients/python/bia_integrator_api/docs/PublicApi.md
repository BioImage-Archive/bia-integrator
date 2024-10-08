# bia_integrator_api.PublicApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_annotation_file_reference**](PublicApi.md#get_annotation_file_reference) | **GET** /v2/annotation_file_reference/{uuid} | Get AnnotationFileReference
[**get_annotation_file_reference_in_annotation_method**](PublicApi.md#get_annotation_file_reference_in_annotation_method) | **GET** /v2/annotation_method/{uuid}/annotation_file_reference | Get AnnotationFileReference In AnnotationMethod
[**get_annotation_file_reference_in_derived_image**](PublicApi.md#get_annotation_file_reference_in_derived_image) | **GET** /v2/derived_image/{uuid}/annotation_file_reference | Get AnnotationFileReference In DerivedImage
[**get_annotation_file_reference_in_experimental_imaging_dataset**](PublicApi.md#get_annotation_file_reference_in_experimental_imaging_dataset) | **GET** /v2/experimental_imaging_dataset/{uuid}/annotation_file_reference | Get AnnotationFileReference In ExperimentalImagingDataset
[**get_annotation_file_reference_in_experimentally_captured_image**](PublicApi.md#get_annotation_file_reference_in_experimentally_captured_image) | **GET** /v2/experimentally_captured_image/{uuid}/annotation_file_reference | Get AnnotationFileReference In ExperimentallyCapturedImage
[**get_annotation_file_reference_in_image_annotation_dataset**](PublicApi.md#get_annotation_file_reference_in_image_annotation_dataset) | **GET** /v2/image_annotation_dataset/{uuid}/annotation_file_reference | Get AnnotationFileReference In ImageAnnotationDataset
[**get_annotation_method**](PublicApi.md#get_annotation_method) | **GET** /v2/annotation_method/{uuid} | Get AnnotationMethod
[**get_bio_sample**](PublicApi.md#get_bio_sample) | **GET** /v2/bio_sample/{uuid} | Get BioSample
[**get_derived_image**](PublicApi.md#get_derived_image) | **GET** /v2/derived_image/{uuid} | Get DerivedImage
[**get_derived_image_in_annotation_method**](PublicApi.md#get_derived_image_in_annotation_method) | **GET** /v2/annotation_method/{uuid}/derived_image | Get DerivedImage In AnnotationMethod
[**get_derived_image_in_derived_image**](PublicApi.md#get_derived_image_in_derived_image) | **GET** /v2/derived_image/{uuid}/derived_image | Get DerivedImage In DerivedImage
[**get_derived_image_in_experimentally_captured_image**](PublicApi.md#get_derived_image_in_experimentally_captured_image) | **GET** /v2/experimentally_captured_image/{uuid}/derived_image | Get DerivedImage In ExperimentallyCapturedImage
[**get_derived_image_in_image_annotation_dataset**](PublicApi.md#get_derived_image_in_image_annotation_dataset) | **GET** /v2/image_annotation_dataset/{uuid}/derived_image | Get DerivedImage In ImageAnnotationDataset
[**get_experimental_imaging_dataset**](PublicApi.md#get_experimental_imaging_dataset) | **GET** /v2/experimental_imaging_dataset/{uuid} | Get ExperimentalImagingDataset
[**get_experimental_imaging_dataset_in_study**](PublicApi.md#get_experimental_imaging_dataset_in_study) | **GET** /v2/study/{uuid}/experimental_imaging_dataset | Get ExperimentalImagingDataset In Study
[**get_experimentally_captured_image**](PublicApi.md#get_experimentally_captured_image) | **GET** /v2/experimentally_captured_image/{uuid} | Get ExperimentallyCapturedImage
[**get_experimentally_captured_image_in_experimental_imaging_dataset**](PublicApi.md#get_experimentally_captured_image_in_experimental_imaging_dataset) | **GET** /v2/experimental_imaging_dataset/{uuid}/experimentally_captured_image | Get ExperimentallyCapturedImage In ExperimentalImagingDataset
[**get_experimentally_captured_image_in_image_acquisition**](PublicApi.md#get_experimentally_captured_image_in_image_acquisition) | **GET** /v2/image_acquisition/{uuid}/experimentally_captured_image | Get ExperimentallyCapturedImage In ImageAcquisition
[**get_experimentally_captured_image_in_specimen**](PublicApi.md#get_experimentally_captured_image_in_specimen) | **GET** /v2/specimen/{uuid}/experimentally_captured_image | Get ExperimentallyCapturedImage In Specimen
[**get_file_reference**](PublicApi.md#get_file_reference) | **GET** /v2/file_reference/{uuid} | Get FileReference
[**get_file_reference_in_experimental_imaging_dataset**](PublicApi.md#get_file_reference_in_experimental_imaging_dataset) | **GET** /v2/experimental_imaging_dataset/{uuid}/file_reference | Get FileReference In ExperimentalImagingDataset
[**get_file_reference_in_image_annotation_dataset**](PublicApi.md#get_file_reference_in_image_annotation_dataset) | **GET** /v2/image_annotation_dataset/{uuid}/file_reference | Get FileReference In ImageAnnotationDataset
[**get_image_acquisition**](PublicApi.md#get_image_acquisition) | **GET** /v2/image_acquisition/{uuid} | Get ImageAcquisition
[**get_image_annotation_dataset**](PublicApi.md#get_image_annotation_dataset) | **GET** /v2/image_annotation_dataset/{uuid} | Get ImageAnnotationDataset
[**get_image_annotation_dataset_in_study**](PublicApi.md#get_image_annotation_dataset_in_study) | **GET** /v2/study/{uuid}/image_annotation_dataset | Get ImageAnnotationDataset In Study
[**get_image_representation**](PublicApi.md#get_image_representation) | **GET** /v2/image_representation/{uuid} | Get ImageRepresentation
[**get_image_representation_in_derived_image**](PublicApi.md#get_image_representation_in_derived_image) | **GET** /v2/derived_image/{uuid}/image_representation | Get ImageRepresentation In DerivedImage
[**get_image_representation_in_experimentally_captured_image**](PublicApi.md#get_image_representation_in_experimentally_captured_image) | **GET** /v2/experimentally_captured_image/{uuid}/image_representation | Get ImageRepresentation In ExperimentallyCapturedImage
[**get_image_representation_in_file_reference**](PublicApi.md#get_image_representation_in_file_reference) | **GET** /v2/file_reference/{uuid}/image_representation | Get ImageRepresentation In FileReference
[**get_specimen**](PublicApi.md#get_specimen) | **GET** /v2/specimen/{uuid} | Get Specimen
[**get_specimen_growth_protocol**](PublicApi.md#get_specimen_growth_protocol) | **GET** /v2/specimen_growth_protocol/{uuid} | Get SpecimenGrowthProtocol
[**get_specimen_imaging_preparation_protocol**](PublicApi.md#get_specimen_imaging_preparation_protocol) | **GET** /v2/specimen_imaging_preparation_protocol/{uuid} | Get SpecimenImagingPreparationProtocol
[**get_specimen_in_bio_sample**](PublicApi.md#get_specimen_in_bio_sample) | **GET** /v2/bio_sample/{uuid}/specimen | Get Specimen In BioSample
[**get_specimen_in_specimen_growth_protocol**](PublicApi.md#get_specimen_in_specimen_growth_protocol) | **GET** /v2/specimen_growth_protocol/{uuid}/specimen | Get Specimen In SpecimenGrowthProtocol
[**get_specimen_in_specimen_imaging_preparation_protocol**](PublicApi.md#get_specimen_in_specimen_imaging_preparation_protocol) | **GET** /v2/specimen_imaging_preparation_protocol/{uuid}/specimen | Get Specimen In SpecimenImagingPreparationProtocol
[**get_studies**](PublicApi.md#get_studies) | **GET** /v2/study | Getstudies
[**get_study**](PublicApi.md#get_study) | **GET** /v2/study/{uuid} | Get Study
[**search_image_representation_by_file_uri**](PublicApi.md#search_image_representation_by_file_uri) | **GET** /v2/search/image_representation/file_uri_fragment | Searchimagerepresentationbyfileuri
[**search_study_by_accession**](PublicApi.md#search_study_by_accession) | **GET** /v2/search/study/accession | Searchstudybyaccession


# **get_annotation_file_reference**
> AnnotationFileReference get_annotation_file_reference(uuid)

Get AnnotationFileReference

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_file_reference import AnnotationFileReference
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get AnnotationFileReference
        api_response = api_instance.get_annotation_file_reference(uuid)
        print("The response of PublicApi->get_annotation_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**AnnotationFileReference**](AnnotationFileReference.md)

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

# **get_annotation_file_reference_in_annotation_method**
> List[AnnotationFileReference] get_annotation_file_reference_in_annotation_method(uuid, page_size, start_uuid=start_uuid)

Get AnnotationFileReference In AnnotationMethod

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_file_reference import AnnotationFileReference
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get AnnotationFileReference In AnnotationMethod
        api_response = api_instance.get_annotation_file_reference_in_annotation_method(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_annotation_file_reference_in_annotation_method:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_file_reference_in_annotation_method: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationFileReference]**](AnnotationFileReference.md)

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

# **get_annotation_file_reference_in_derived_image**
> List[AnnotationFileReference] get_annotation_file_reference_in_derived_image(uuid, page_size, start_uuid=start_uuid)

Get AnnotationFileReference In DerivedImage

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_file_reference import AnnotationFileReference
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get AnnotationFileReference In DerivedImage
        api_response = api_instance.get_annotation_file_reference_in_derived_image(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_annotation_file_reference_in_derived_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_file_reference_in_derived_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationFileReference]**](AnnotationFileReference.md)

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

# **get_annotation_file_reference_in_experimental_imaging_dataset**
> List[AnnotationFileReference] get_annotation_file_reference_in_experimental_imaging_dataset(uuid, page_size, start_uuid=start_uuid)

Get AnnotationFileReference In ExperimentalImagingDataset

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_file_reference import AnnotationFileReference
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get AnnotationFileReference In ExperimentalImagingDataset
        api_response = api_instance.get_annotation_file_reference_in_experimental_imaging_dataset(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_annotation_file_reference_in_experimental_imaging_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_file_reference_in_experimental_imaging_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationFileReference]**](AnnotationFileReference.md)

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

# **get_annotation_file_reference_in_experimentally_captured_image**
> List[AnnotationFileReference] get_annotation_file_reference_in_experimentally_captured_image(uuid, page_size, start_uuid=start_uuid)

Get AnnotationFileReference In ExperimentallyCapturedImage

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_file_reference import AnnotationFileReference
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get AnnotationFileReference In ExperimentallyCapturedImage
        api_response = api_instance.get_annotation_file_reference_in_experimentally_captured_image(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_annotation_file_reference_in_experimentally_captured_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_file_reference_in_experimentally_captured_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationFileReference]**](AnnotationFileReference.md)

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

# **get_annotation_file_reference_in_image_annotation_dataset**
> List[AnnotationFileReference] get_annotation_file_reference_in_image_annotation_dataset(uuid, page_size, start_uuid=start_uuid)

Get AnnotationFileReference In ImageAnnotationDataset

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.annotation_file_reference import AnnotationFileReference
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get AnnotationFileReference In ImageAnnotationDataset
        api_response = api_instance.get_annotation_file_reference_in_image_annotation_dataset(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_annotation_file_reference_in_image_annotation_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_file_reference_in_image_annotation_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[AnnotationFileReference]**](AnnotationFileReference.md)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get AnnotationMethod
        api_response = api_instance.get_annotation_method(uuid)
        print("The response of PublicApi->get_annotation_method:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_annotation_method: %s\n" % e)
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get BioSample
        api_response = api_instance.get_bio_sample(uuid)
        print("The response of PublicApi->get_bio_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_bio_sample: %s\n" % e)
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

# **get_derived_image**
> DerivedImage get_derived_image(uuid)

Get DerivedImage

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.derived_image import DerivedImage
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get DerivedImage
        api_response = api_instance.get_derived_image(uuid)
        print("The response of PublicApi->get_derived_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_derived_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**DerivedImage**](DerivedImage.md)

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

# **get_derived_image_in_annotation_method**
> List[DerivedImage] get_derived_image_in_annotation_method(uuid, page_size, start_uuid=start_uuid)

Get DerivedImage In AnnotationMethod

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.derived_image import DerivedImage
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get DerivedImage In AnnotationMethod
        api_response = api_instance.get_derived_image_in_annotation_method(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_derived_image_in_annotation_method:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_derived_image_in_annotation_method: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[DerivedImage]**](DerivedImage.md)

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

# **get_derived_image_in_derived_image**
> List[DerivedImage] get_derived_image_in_derived_image(uuid, page_size, start_uuid=start_uuid)

Get DerivedImage In DerivedImage

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.derived_image import DerivedImage
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get DerivedImage In DerivedImage
        api_response = api_instance.get_derived_image_in_derived_image(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_derived_image_in_derived_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_derived_image_in_derived_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[DerivedImage]**](DerivedImage.md)

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

# **get_derived_image_in_experimentally_captured_image**
> List[DerivedImage] get_derived_image_in_experimentally_captured_image(uuid, page_size, start_uuid=start_uuid)

Get DerivedImage In ExperimentallyCapturedImage

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.derived_image import DerivedImage
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get DerivedImage In ExperimentallyCapturedImage
        api_response = api_instance.get_derived_image_in_experimentally_captured_image(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_derived_image_in_experimentally_captured_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_derived_image_in_experimentally_captured_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[DerivedImage]**](DerivedImage.md)

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

# **get_derived_image_in_image_annotation_dataset**
> List[DerivedImage] get_derived_image_in_image_annotation_dataset(uuid, page_size, start_uuid=start_uuid)

Get DerivedImage In ImageAnnotationDataset

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.derived_image import DerivedImage
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get DerivedImage In ImageAnnotationDataset
        api_response = api_instance.get_derived_image_in_image_annotation_dataset(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_derived_image_in_image_annotation_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_derived_image_in_image_annotation_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[DerivedImage]**](DerivedImage.md)

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

# **get_experimental_imaging_dataset**
> ExperimentalImagingDataset get_experimental_imaging_dataset(uuid)

Get ExperimentalImagingDataset

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.experimental_imaging_dataset import ExperimentalImagingDataset
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get ExperimentalImagingDataset
        api_response = api_instance.get_experimental_imaging_dataset(uuid)
        print("The response of PublicApi->get_experimental_imaging_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_experimental_imaging_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**ExperimentalImagingDataset**](ExperimentalImagingDataset.md)

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

# **get_experimental_imaging_dataset_in_study**
> List[ExperimentalImagingDataset] get_experimental_imaging_dataset_in_study(uuid, page_size, start_uuid=start_uuid)

Get ExperimentalImagingDataset In Study

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.experimental_imaging_dataset import ExperimentalImagingDataset
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get ExperimentalImagingDataset In Study
        api_response = api_instance.get_experimental_imaging_dataset_in_study(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_experimental_imaging_dataset_in_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_experimental_imaging_dataset_in_study: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[ExperimentalImagingDataset]**](ExperimentalImagingDataset.md)

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

# **get_experimentally_captured_image**
> ExperimentallyCapturedImage get_experimentally_captured_image(uuid)

Get ExperimentallyCapturedImage

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.experimentally_captured_image import ExperimentallyCapturedImage
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get ExperimentallyCapturedImage
        api_response = api_instance.get_experimentally_captured_image(uuid)
        print("The response of PublicApi->get_experimentally_captured_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_experimentally_captured_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**ExperimentallyCapturedImage**](ExperimentallyCapturedImage.md)

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

# **get_experimentally_captured_image_in_experimental_imaging_dataset**
> List[ExperimentallyCapturedImage] get_experimentally_captured_image_in_experimental_imaging_dataset(uuid, page_size, start_uuid=start_uuid)

Get ExperimentallyCapturedImage In ExperimentalImagingDataset

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.experimentally_captured_image import ExperimentallyCapturedImage
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get ExperimentallyCapturedImage In ExperimentalImagingDataset
        api_response = api_instance.get_experimentally_captured_image_in_experimental_imaging_dataset(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_experimentally_captured_image_in_experimental_imaging_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_experimentally_captured_image_in_experimental_imaging_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[ExperimentallyCapturedImage]**](ExperimentallyCapturedImage.md)

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

# **get_experimentally_captured_image_in_image_acquisition**
> List[ExperimentallyCapturedImage] get_experimentally_captured_image_in_image_acquisition(uuid, page_size, start_uuid=start_uuid)

Get ExperimentallyCapturedImage In ImageAcquisition

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.experimentally_captured_image import ExperimentallyCapturedImage
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get ExperimentallyCapturedImage In ImageAcquisition
        api_response = api_instance.get_experimentally_captured_image_in_image_acquisition(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_experimentally_captured_image_in_image_acquisition:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_experimentally_captured_image_in_image_acquisition: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[ExperimentallyCapturedImage]**](ExperimentallyCapturedImage.md)

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

# **get_experimentally_captured_image_in_specimen**
> List[ExperimentallyCapturedImage] get_experimentally_captured_image_in_specimen(uuid, page_size, start_uuid=start_uuid)

Get ExperimentallyCapturedImage In Specimen

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.experimentally_captured_image import ExperimentallyCapturedImage
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get ExperimentallyCapturedImage In Specimen
        api_response = api_instance.get_experimentally_captured_image_in_specimen(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_experimentally_captured_image_in_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_experimentally_captured_image_in_specimen: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[ExperimentallyCapturedImage]**](ExperimentallyCapturedImage.md)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get FileReference
        api_response = api_instance.get_file_reference(uuid)
        print("The response of PublicApi->get_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_file_reference: %s\n" % e)
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

# **get_file_reference_in_experimental_imaging_dataset**
> List[FileReference] get_file_reference_in_experimental_imaging_dataset(uuid, page_size, start_uuid=start_uuid)

Get FileReference In ExperimentalImagingDataset

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get FileReference In ExperimentalImagingDataset
        api_response = api_instance.get_file_reference_in_experimental_imaging_dataset(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_file_reference_in_experimental_imaging_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_file_reference_in_experimental_imaging_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

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

# **get_file_reference_in_image_annotation_dataset**
> List[FileReference] get_file_reference_in_image_annotation_dataset(uuid, page_size, start_uuid=start_uuid)

Get FileReference In ImageAnnotationDataset

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get FileReference In ImageAnnotationDataset
        api_response = api_instance.get_file_reference_in_image_annotation_dataset(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_file_reference_in_image_annotation_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_file_reference_in_image_annotation_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

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

# **get_image_acquisition**
> ImageAcquisition get_image_acquisition(uuid)

Get ImageAcquisition

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_acquisition import ImageAcquisition
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get ImageAcquisition
        api_response = api_instance.get_image_acquisition(uuid)
        print("The response of PublicApi->get_image_acquisition:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_acquisition: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**ImageAcquisition**](ImageAcquisition.md)

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

# **get_image_annotation_dataset**
> ImageAnnotationDataset get_image_annotation_dataset(uuid)

Get ImageAnnotationDataset

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_annotation_dataset import ImageAnnotationDataset
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get ImageAnnotationDataset
        api_response = api_instance.get_image_annotation_dataset(uuid)
        print("The response of PublicApi->get_image_annotation_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_annotation_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**ImageAnnotationDataset**](ImageAnnotationDataset.md)

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

# **get_image_annotation_dataset_in_study**
> List[ImageAnnotationDataset] get_image_annotation_dataset_in_study(uuid, page_size, start_uuid=start_uuid)

Get ImageAnnotationDataset In Study

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.image_annotation_dataset import ImageAnnotationDataset
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get ImageAnnotationDataset In Study
        api_response = api_instance.get_image_annotation_dataset_in_study(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_image_annotation_dataset_in_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_annotation_dataset_in_study: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

### Return type

[**List[ImageAnnotationDataset]**](ImageAnnotationDataset.md)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get ImageRepresentation
        api_response = api_instance.get_image_representation(uuid)
        print("The response of PublicApi->get_image_representation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_representation: %s\n" % e)
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

# **get_image_representation_in_derived_image**
> List[ImageRepresentation] get_image_representation_in_derived_image(uuid, page_size, start_uuid=start_uuid)

Get ImageRepresentation In DerivedImage

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get ImageRepresentation In DerivedImage
        api_response = api_instance.get_image_representation_in_derived_image(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_image_representation_in_derived_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_representation_in_derived_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

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

# **get_image_representation_in_experimentally_captured_image**
> List[ImageRepresentation] get_image_representation_in_experimentally_captured_image(uuid, page_size, start_uuid=start_uuid)

Get ImageRepresentation In ExperimentallyCapturedImage

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get ImageRepresentation In ExperimentallyCapturedImage
        api_response = api_instance.get_image_representation_in_experimentally_captured_image(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_image_representation_in_experimentally_captured_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_representation_in_experimentally_captured_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

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

# **get_image_representation_in_file_reference**
> List[ImageRepresentation] get_image_representation_in_file_reference(uuid, page_size, start_uuid=start_uuid)

Get ImageRepresentation In FileReference

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get ImageRepresentation In FileReference
        api_response = api_instance.get_image_representation_in_file_reference(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_image_representation_in_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_representation_in_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Specimen
        api_response = api_instance.get_specimen(uuid)
        print("The response of PublicApi->get_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen: %s\n" % e)
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

# **get_specimen_growth_protocol**
> SpecimenGrowthProtocol get_specimen_growth_protocol(uuid)

Get SpecimenGrowthProtocol

### Example


```python
import bia_integrator_api
from bia_integrator_api.models.specimen_growth_protocol import SpecimenGrowthProtocol
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get SpecimenGrowthProtocol
        api_response = api_instance.get_specimen_growth_protocol(uuid)
        print("The response of PublicApi->get_specimen_growth_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen_growth_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 

### Return type

[**SpecimenGrowthProtocol**](SpecimenGrowthProtocol.md)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get SpecimenImagingPreparationProtocol
        api_response = api_instance.get_specimen_imaging_preparation_protocol(uuid)
        print("The response of PublicApi->get_specimen_imaging_preparation_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen_imaging_preparation_protocol: %s\n" % e)
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

# **get_specimen_in_bio_sample**
> List[Specimen] get_specimen_in_bio_sample(uuid, page_size, start_uuid=start_uuid)

Get Specimen In BioSample

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get Specimen In BioSample
        api_response = api_instance.get_specimen_in_bio_sample(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_specimen_in_bio_sample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen_in_bio_sample: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

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

# **get_specimen_in_specimen_growth_protocol**
> List[Specimen] get_specimen_in_specimen_growth_protocol(uuid, page_size, start_uuid=start_uuid)

Get Specimen In SpecimenGrowthProtocol

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get Specimen In SpecimenGrowthProtocol
        api_response = api_instance.get_specimen_in_specimen_growth_protocol(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_specimen_in_specimen_growth_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen_in_specimen_growth_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

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

# **get_specimen_in_specimen_imaging_preparation_protocol**
> List[Specimen] get_specimen_in_specimen_imaging_preparation_protocol(uuid, page_size, start_uuid=start_uuid)

Get Specimen In SpecimenImagingPreparationProtocol

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Get Specimen In SpecimenImagingPreparationProtocol
        api_response = api_instance.get_specimen_in_specimen_imaging_preparation_protocol(uuid, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_specimen_in_specimen_imaging_preparation_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_specimen_in_specimen_imaging_preparation_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **uuid** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

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
> List[Study] get_studies(page_size, start_uuid=start_uuid)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Getstudies
        api_response = api_instance.get_studies(page_size, start_uuid=start_uuid)
        print("The response of PublicApi->get_studies:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_studies: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    uuid = 'uuid_example' # str | 

    try:
        # Get Study
        api_response = api_instance.get_study(uuid)
        print("The response of PublicApi->get_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_study: %s\n" % e)
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

# **search_image_representation_by_file_uri**
> List[ImageRepresentation] search_image_representation_by_file_uri(file_uri, page_size, start_uuid=start_uuid)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    file_uri = 'file_uri_example' # str | 
    page_size = 56 # int | 
    start_uuid = 'start_uuid_example' # str |  (optional)

    try:
        # Searchimagerepresentationbyfileuri
        api_response = api_instance.search_image_representation_by_file_uri(file_uri, page_size, start_uuid=start_uuid)
        print("The response of PublicApi->search_image_representation_by_file_uri:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_image_representation_by_file_uri: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_uri** | **str**|  | 
 **page_size** | **int**|  | 
 **start_uuid** | **str**|  | [optional] 

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    accession_id = 'accession_id_example' # str | 

    try:
        # Searchstudybyaccession
        api_response = api_instance.search_study_by_accession(accession_id)
        print("The response of PublicApi->search_study_by_accession:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_study_by_accession: %s\n" % e)
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

