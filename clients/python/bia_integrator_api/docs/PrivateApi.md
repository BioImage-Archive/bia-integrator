# bia_integrator_api.PrivateApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**login_for_access_token**](PrivateApi.md#login_for_access_token) | **POST** /v2/auth/token | Login For Access Token
[**post_annotation_file_reference**](PrivateApi.md#post_annotation_file_reference) | **POST** /v2/private/annotation_file_reference | Create AnnotationFileReference
[**post_annotation_method**](PrivateApi.md#post_annotation_method) | **POST** /v2/private/annotation_method | Create AnnotationMethod
[**post_bio_sample**](PrivateApi.md#post_bio_sample) | **POST** /v2/private/bio_sample | Create BioSample
[**post_derived_image**](PrivateApi.md#post_derived_image) | **POST** /v2/private/derived_image | Create DerivedImage
[**post_experimental_imaging_dataset**](PrivateApi.md#post_experimental_imaging_dataset) | **POST** /v2/private/experimental_imaging_dataset | Create ExperimentalImagingDataset
[**post_experimentally_captured_image**](PrivateApi.md#post_experimentally_captured_image) | **POST** /v2/private/experimentally_captured_image | Create ExperimentallyCapturedImage
[**post_file_reference**](PrivateApi.md#post_file_reference) | **POST** /v2/private/file_reference | Create FileReference
[**post_image_acquisition**](PrivateApi.md#post_image_acquisition) | **POST** /v2/private/image_acquisition | Create ImageAcquisition
[**post_image_annotation_dataset**](PrivateApi.md#post_image_annotation_dataset) | **POST** /v2/private/image_annotation_dataset | Create ImageAnnotationDataset
[**post_image_representation**](PrivateApi.md#post_image_representation) | **POST** /v2/private/image_representation | Create ImageRepresentation
[**post_specimen**](PrivateApi.md#post_specimen) | **POST** /v2/private/specimen | Create Specimen
[**post_specimen_growth_protocol**](PrivateApi.md#post_specimen_growth_protocol) | **POST** /v2/private/specimen_growth_protocol | Create SpecimenGrowthProtocol
[**post_specimen_imaging_preparation_protocol**](PrivateApi.md#post_specimen_imaging_preparation_protocol) | **POST** /v2/private/specimen_imaging_preparation_protocol | Create SpecimenImagingPreparationProtocol
[**post_study**](PrivateApi.md#post_study) | **POST** /v2/private/study | Create Study
[**register_user**](PrivateApi.md#register_user) | **POST** /v2/auth/user/register | Register User


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

# **post_annotation_file_reference**
> object post_annotation_file_reference(annotation_file_reference)

Create AnnotationFileReference

### Example

* OAuth Authentication (OAuth2PasswordBearer):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    annotation_file_reference = bia_integrator_api.AnnotationFileReference() # AnnotationFileReference | 

    try:
        # Create AnnotationFileReference
        api_response = api_instance.post_annotation_file_reference(annotation_file_reference)
        print("The response of PrivateApi->post_annotation_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_annotation_file_reference: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **annotation_file_reference** | [**AnnotationFileReference**](AnnotationFileReference.md)|  | 

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

# **post_derived_image**
> object post_derived_image(derived_image)

Create DerivedImage

### Example

* OAuth Authentication (OAuth2PasswordBearer):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    derived_image = bia_integrator_api.DerivedImage() # DerivedImage | 

    try:
        # Create DerivedImage
        api_response = api_instance.post_derived_image(derived_image)
        print("The response of PrivateApi->post_derived_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_derived_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **derived_image** | [**DerivedImage**](DerivedImage.md)|  | 

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

# **post_experimental_imaging_dataset**
> object post_experimental_imaging_dataset(experimental_imaging_dataset)

Create ExperimentalImagingDataset

### Example

* OAuth Authentication (OAuth2PasswordBearer):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    experimental_imaging_dataset = bia_integrator_api.ExperimentalImagingDataset() # ExperimentalImagingDataset | 

    try:
        # Create ExperimentalImagingDataset
        api_response = api_instance.post_experimental_imaging_dataset(experimental_imaging_dataset)
        print("The response of PrivateApi->post_experimental_imaging_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_experimental_imaging_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **experimental_imaging_dataset** | [**ExperimentalImagingDataset**](ExperimentalImagingDataset.md)|  | 

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

# **post_experimentally_captured_image**
> object post_experimentally_captured_image(experimentally_captured_image)

Create ExperimentallyCapturedImage

### Example

* OAuth Authentication (OAuth2PasswordBearer):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    experimentally_captured_image = bia_integrator_api.ExperimentallyCapturedImage() # ExperimentallyCapturedImage | 

    try:
        # Create ExperimentallyCapturedImage
        api_response = api_instance.post_experimentally_captured_image(experimentally_captured_image)
        print("The response of PrivateApi->post_experimentally_captured_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_experimentally_captured_image: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **experimentally_captured_image** | [**ExperimentallyCapturedImage**](ExperimentallyCapturedImage.md)|  | 

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

# **post_image_acquisition**
> object post_image_acquisition(image_acquisition)

Create ImageAcquisition

### Example

* OAuth Authentication (OAuth2PasswordBearer):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    image_acquisition = bia_integrator_api.ImageAcquisition() # ImageAcquisition | 

    try:
        # Create ImageAcquisition
        api_response = api_instance.post_image_acquisition(image_acquisition)
        print("The response of PrivateApi->post_image_acquisition:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_image_acquisition: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_acquisition** | [**ImageAcquisition**](ImageAcquisition.md)|  | 

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

# **post_image_annotation_dataset**
> object post_image_annotation_dataset(image_annotation_dataset)

Create ImageAnnotationDataset

### Example

* OAuth Authentication (OAuth2PasswordBearer):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    image_annotation_dataset = bia_integrator_api.ImageAnnotationDataset() # ImageAnnotationDataset | 

    try:
        # Create ImageAnnotationDataset
        api_response = api_instance.post_image_annotation_dataset(image_annotation_dataset)
        print("The response of PrivateApi->post_image_annotation_dataset:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_image_annotation_dataset: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_annotation_dataset** | [**ImageAnnotationDataset**](ImageAnnotationDataset.md)|  | 

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

# **post_specimen_growth_protocol**
> object post_specimen_growth_protocol(specimen_growth_protocol)

Create SpecimenGrowthProtocol

### Example

* OAuth Authentication (OAuth2PasswordBearer):

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

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PrivateApi(api_client)
    specimen_growth_protocol = bia_integrator_api.SpecimenGrowthProtocol() # SpecimenGrowthProtocol | 

    try:
        # Create SpecimenGrowthProtocol
        api_response = api_instance.post_specimen_growth_protocol(specimen_growth_protocol)
        print("The response of PrivateApi->post_specimen_growth_protocol:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->post_specimen_growth_protocol: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **specimen_growth_protocol** | [**SpecimenGrowthProtocol**](SpecimenGrowthProtocol.md)|  | 

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

