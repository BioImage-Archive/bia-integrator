# bia_integrator_api.PrivateApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_biosample**](PrivateApi.md#create_biosample) | **POST** /v1/private/biosamples | Create Biosample
[**create_collection**](PrivateApi.md#create_collection) | **POST** /v1/private/collections | Create Collection
[**create_file_references**](PrivateApi.md#create_file_references) | **POST** /v1/private/file_references | Create File References
[**create_image_acquisition**](PrivateApi.md#create_image_acquisition) | **POST** /v1/private/image_acquisitions | Create Image Acquisition
[**create_image_representation**](PrivateApi.md#create_image_representation) | **POST** /v1/private/images/{image_uuid}/representations/single | Create Image Representation
[**create_images**](PrivateApi.md#create_images) | **POST** /v1/private/images | Create Images
[**create_images_bulk**](PrivateApi.md#create_images_bulk) | **POST** /v1/private/images/bulk | Create Images Bulk
[**create_specimen**](PrivateApi.md#create_specimen) | **POST** /v1/private/specimens | Create Specimen
[**create_study**](PrivateApi.md#create_study) | **POST** /v1/private/studies | Create Study
[**get_biosample**](PrivateApi.md#get_biosample) | **GET** /v1/biosamples/{biosample_uuid} | Get Biosample
[**get_collection**](PrivateApi.md#get_collection) | **GET** /v1/collections/{collection_uuid} | Get Collection
[**get_file_reference**](PrivateApi.md#get_file_reference) | **GET** /v1/file_references/{file_reference_uuid} | Get File Reference
[**get_image**](PrivateApi.md#get_image) | **GET** /v1/images/{image_uuid} | Get Image
[**get_image_acquisition**](PrivateApi.md#get_image_acquisition) | **GET** /v1/image_acquisitions/{image_acquisition_uuid} | Get Image Acquisition
[**get_image_ome_metadata**](PrivateApi.md#get_image_ome_metadata) | **GET** /v1/images/{image_uuid}/ome_metadata | Get Image Ome Metadata
[**get_object_info_by_accession**](PrivateApi.md#get_object_info_by_accession) | **GET** /v1/object_info_by_accessions | Get Object Info By Accession
[**get_specimen**](PrivateApi.md#get_specimen) | **GET** /v1/specimens/{specimen_uuid} | Get Specimen
[**get_study**](PrivateApi.md#get_study) | **GET** /v1/studies/{study_uuid} | Get Study
[**get_study_file_references**](PrivateApi.md#get_study_file_references) | **GET** /v1/studies/{study_uuid}/file_references | Get Study File References
[**get_study_images**](PrivateApi.md#get_study_images) | **GET** /v1/studies/{study_uuid}/images | Get Study Images
[**get_study_images_by_alias**](PrivateApi.md#get_study_images_by_alias) | **GET** /v1/studies/{study_accession}/images_by_aliases | Get Study Images By Alias
[**health_check**](PrivateApi.md#health_check) | **GET** /v1/admin/health-check | Health Check
[**login_for_access_token**](PrivateApi.md#login_for_access_token) | **POST** /v1/auth/token | Login For Access Token
[**register_user**](PrivateApi.md#register_user) | **POST** /v1/auth/users/register | Register User
[**search_collections**](PrivateApi.md#search_collections) | **GET** /v1/collections | Search Collections
[**search_file_references_exact_match**](PrivateApi.md#search_file_references_exact_match) | **POST** /v1/search/file_references/exact_match | Search File References Exact Match
[**search_images_exact_match**](PrivateApi.md#search_images_exact_match) | **POST** /v1/search/images/exact_match | Search Images Exact Match
[**search_studies**](PrivateApi.md#search_studies) | **GET** /v1/search/studies | Search Studies
[**search_studies_exact_match**](PrivateApi.md#search_studies_exact_match) | **POST** /v1/search/studies/exact_match | Search Studies Exact Match
[**set_image_ome_metadata**](PrivateApi.md#set_image_ome_metadata) | **POST** /v1/private/images/{image_uuid}/ome_metadata | Set Image Ome Metadata
[**study_refresh_counts**](PrivateApi.md#study_refresh_counts) | **POST** /v1/private/studies/{study_uuid}/refresh_counts | Study Refresh Counts
[**update_biosample**](PrivateApi.md#update_biosample) | **PATCH** /v1/private/biosamples | Update Biosample
[**update_file_reference**](PrivateApi.md#update_file_reference) | **PATCH** /v1/private/file_references/single | Update File Reference
[**update_image**](PrivateApi.md#update_image) | **PATCH** /v1/private/images/single | Update Image
[**update_image_acquisition**](PrivateApi.md#update_image_acquisition) | **PATCH** /v1/private/image_acquisitions | Update Image Acquisition
[**update_specimen**](PrivateApi.md#update_specimen) | **PATCH** /v1/private/specimens | Update Specimen
[**update_study**](PrivateApi.md#update_study) | **PATCH** /v1/private/studies | Update Study


# **create_biosample**
> object create_biosample(biosample, overwrite_mode=overwrite_mode)

Create Biosample

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.biosample import Biosample
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
    biosample = bia_integrator_api.Biosample() # Biosample | 
    overwrite_mode = bia_integrator_api.OverwriteMode() # OverwriteMode |  (optional)

    try:
        # Create Biosample
        api_response = api_instance.create_biosample(biosample, overwrite_mode=overwrite_mode)
        print("The response of PrivateApi->create_biosample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->create_biosample: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **biosample** | [**Biosample**](Biosample.md)|  | 
 **overwrite_mode** | [**OverwriteMode**](.md)|  | [optional] 

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

# **create_collection**
> object create_collection(bia_collection, overwrite_mode=overwrite_mode)

Create Collection

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_collection import BIACollection
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
    bia_collection = bia_integrator_api.BIACollection() # BIACollection | 
    overwrite_mode = bia_integrator_api.OverwriteMode() # OverwriteMode |  (optional)

    try:
        # Create Collection
        api_response = api_instance.create_collection(bia_collection, overwrite_mode=overwrite_mode)
        print("The response of PrivateApi->create_collection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->create_collection: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bia_collection** | [**BIACollection**](BIACollection.md)|  | 
 **overwrite_mode** | [**OverwriteMode**](.md)|  | [optional] 

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

# **create_file_references**
> BulkOperationResponse create_file_references(file_reference, overwrite_mode=overwrite_mode)

Create File References

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bulk_operation_response import BulkOperationResponse
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
    file_reference = [bia_integrator_api.FileReference()] # List[FileReference] | 
    overwrite_mode = bia_integrator_api.OverwriteMode() # OverwriteMode |  (optional)

    try:
        # Create File References
        api_response = api_instance.create_file_references(file_reference, overwrite_mode=overwrite_mode)
        print("The response of PrivateApi->create_file_references:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->create_file_references: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_reference** | [**List[FileReference]**](FileReference.md)|  | 
 **overwrite_mode** | [**OverwriteMode**](.md)|  | [optional] 

### Return type

[**BulkOperationResponse**](BulkOperationResponse.md)

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

# **create_image_acquisition**
> object create_image_acquisition(image_acquisition, overwrite_mode=overwrite_mode)

Create Image Acquisition

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
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
    overwrite_mode = bia_integrator_api.OverwriteMode() # OverwriteMode |  (optional)

    try:
        # Create Image Acquisition
        api_response = api_instance.create_image_acquisition(image_acquisition, overwrite_mode=overwrite_mode)
        print("The response of PrivateApi->create_image_acquisition:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->create_image_acquisition: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_acquisition** | [**ImageAcquisition**](ImageAcquisition.md)|  | 
 **overwrite_mode** | [**OverwriteMode**](.md)|  | [optional] 

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

# **create_image_representation**
> object create_image_representation(image_uuid, bia_image_representation)

Create Image Representation

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_image_representation import BIAImageRepresentation
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
    image_uuid = 'image_uuid_example' # str | 
    bia_image_representation = bia_integrator_api.BIAImageRepresentation() # BIAImageRepresentation | 

    try:
        # Create Image Representation
        api_response = api_instance.create_image_representation(image_uuid, bia_image_representation)
        print("The response of PrivateApi->create_image_representation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->create_image_representation: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_uuid** | **str**|  | 
 **bia_image_representation** | [**BIAImageRepresentation**](BIAImageRepresentation.md)|  | 

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

# **create_images**
> BulkOperationResponse create_images(bia_image, overwrite_mode=overwrite_mode)

Create Images

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_image import BIAImage
from bia_integrator_api.models.bulk_operation_response import BulkOperationResponse
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
    bia_image = [bia_integrator_api.BIAImage()] # List[BIAImage] | 
    overwrite_mode = bia_integrator_api.OverwriteMode() # OverwriteMode |  (optional)

    try:
        # Create Images
        api_response = api_instance.create_images(bia_image, overwrite_mode=overwrite_mode)
        print("The response of PrivateApi->create_images:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->create_images: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bia_image** | [**List[BIAImage]**](BIAImage.md)|  | 
 **overwrite_mode** | [**OverwriteMode**](.md)|  | [optional] 

### Return type

[**BulkOperationResponse**](BulkOperationResponse.md)

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

# **create_images_bulk**
> object create_images_bulk()

Create Images Bulk

TODO: Maybe file-based async?

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
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

    try:
        # Create Images Bulk
        api_response = api_instance.create_images_bulk()
        print("The response of PrivateApi->create_images_bulk:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->create_images_bulk: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **create_specimen**
> object create_specimen(specimen, overwrite_mode=overwrite_mode)

Create Specimen

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
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
    overwrite_mode = bia_integrator_api.OverwriteMode() # OverwriteMode |  (optional)

    try:
        # Create Specimen
        api_response = api_instance.create_specimen(specimen, overwrite_mode=overwrite_mode)
        print("The response of PrivateApi->create_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->create_specimen: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **specimen** | [**Specimen**](Specimen.md)|  | 
 **overwrite_mode** | [**OverwriteMode**](.md)|  | [optional] 

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

# **create_study**
> object create_study(bia_study, overwrite_mode=overwrite_mode)

Create Study

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_study import BIAStudy
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
    bia_study = bia_integrator_api.BIAStudy() # BIAStudy | 
    overwrite_mode = bia_integrator_api.OverwriteMode() # OverwriteMode |  (optional)

    try:
        # Create Study
        api_response = api_instance.create_study(bia_study, overwrite_mode=overwrite_mode)
        print("The response of PrivateApi->create_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->create_study: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bia_study** | [**BIAStudy**](BIAStudy.md)|  | 
 **overwrite_mode** | [**OverwriteMode**](.md)|  | [optional] 

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

# **get_biosample**
> Biosample get_biosample(biosample_uuid)

Get Biosample

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.biosample import Biosample
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
    biosample_uuid = 'biosample_uuid_example' # str | 

    try:
        # Get Biosample
        api_response = api_instance.get_biosample(biosample_uuid)
        print("The response of PrivateApi->get_biosample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_biosample: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **biosample_uuid** | **str**|  | 

### Return type

[**Biosample**](Biosample.md)

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

# **get_collection**
> BIACollection get_collection(collection_uuid, apply_annotations=apply_annotations)

Get Collection

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_collection import BIACollection
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
    collection_uuid = 'collection_uuid_example' # str | 
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Get Collection
        api_response = api_instance.get_collection(collection_uuid, apply_annotations=apply_annotations)
        print("The response of PrivateApi->get_collection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_collection: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_uuid** | **str**|  | 
 **apply_annotations** | **bool**|  | [optional] [default to False]

### Return type

[**BIACollection**](BIACollection.md)

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
> FileReference get_file_reference(file_reference_uuid, apply_annotations=apply_annotations)

Get File Reference

### Example

```python
import time
import os
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
    file_reference_uuid = 'file_reference_uuid_example' # str | 
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Get File Reference
        api_response = api_instance.get_file_reference(file_reference_uuid, apply_annotations=apply_annotations)
        print("The response of PrivateApi->get_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_file_reference: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_reference_uuid** | **str**|  | 
 **apply_annotations** | **bool**|  | [optional] [default to False]

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

# **get_image**
> BIAImage get_image(image_uuid, apply_annotations=apply_annotations)

Get Image

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_image import BIAImage
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
    image_uuid = 'image_uuid_example' # str | 
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Get Image
        api_response = api_instance.get_image(image_uuid, apply_annotations=apply_annotations)
        print("The response of PrivateApi->get_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_image: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_uuid** | **str**|  | 
 **apply_annotations** | **bool**|  | [optional] [default to False]

### Return type

[**BIAImage**](BIAImage.md)

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
> ImageAcquisition get_image_acquisition(image_acquisition_uuid)

Get Image Acquisition

### Example

```python
import time
import os
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
    api_instance = bia_integrator_api.PrivateApi(api_client)
    image_acquisition_uuid = 'image_acquisition_uuid_example' # str | 

    try:
        # Get Image Acquisition
        api_response = api_instance.get_image_acquisition(image_acquisition_uuid)
        print("The response of PrivateApi->get_image_acquisition:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_image_acquisition: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_acquisition_uuid** | **str**|  | 

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

# **get_image_ome_metadata**
> BIAImageOmeMetadata get_image_ome_metadata(image_uuid)

Get Image Ome Metadata

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_image_ome_metadata import BIAImageOmeMetadata
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
    image_uuid = 'image_uuid_example' # str | 

    try:
        # Get Image Ome Metadata
        api_response = api_instance.get_image_ome_metadata(image_uuid)
        print("The response of PrivateApi->get_image_ome_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_image_ome_metadata: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_uuid** | **str**|  | 

### Return type

[**BIAImageOmeMetadata**](BIAImageOmeMetadata.md)

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

# **get_object_info_by_accession**
> List[ObjectInfo] get_object_info_by_accession(accessions)

Get Object Info By Accession

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.object_info import ObjectInfo
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
    accessions = ['accessions_example'] # List[str] | 

    try:
        # Get Object Info By Accession
        api_response = api_instance.get_object_info_by_accession(accessions)
        print("The response of PrivateApi->get_object_info_by_accession:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_object_info_by_accession: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **accessions** | [**List[str]**](str.md)|  | 

### Return type

[**List[ObjectInfo]**](ObjectInfo.md)

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
> Specimen get_specimen(specimen_uuid)

Get Specimen

### Example

```python
import time
import os
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
    specimen_uuid = 'specimen_uuid_example' # str | 

    try:
        # Get Specimen
        api_response = api_instance.get_specimen(specimen_uuid)
        print("The response of PrivateApi->get_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_specimen: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **specimen_uuid** | **str**|  | 

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

# **get_study**
> BIAStudy get_study(study_uuid, apply_annotations=apply_annotations)

Get Study

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_study import BIAStudy
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
    study_uuid = 'study_uuid_example' # str | 
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Get Study
        api_response = api_instance.get_study(study_uuid, apply_annotations=apply_annotations)
        print("The response of PrivateApi->get_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_study: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_uuid** | **str**|  | 
 **apply_annotations** | **bool**|  | [optional] [default to False]

### Return type

[**BIAStudy**](BIAStudy.md)

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

# **get_study_file_references**
> List[FileReference] get_study_file_references(study_uuid, start_uuid=start_uuid, limit=limit, apply_annotations=apply_annotations)

Get Study File References

First item in response is the next item with uuid greater than start_uuid. start_uuid is part of the response

### Example

```python
import time
import os
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
    study_uuid = 'study_uuid_example' # str | 
    start_uuid = bia_integrator_api.StartUuid() # StartUuid |  (optional)
    limit = 10 # int |  (optional) (default to 10)
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Get Study File References
        api_response = api_instance.get_study_file_references(study_uuid, start_uuid=start_uuid, limit=limit, apply_annotations=apply_annotations)
        print("The response of PrivateApi->get_study_file_references:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_study_file_references: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_uuid** | **str**|  | 
 **start_uuid** | [**StartUuid**](.md)|  | [optional] 
 **limit** | **int**|  | [optional] [default to 10]
 **apply_annotations** | **bool**|  | [optional] [default to False]

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

# **get_study_images**
> List[BIAImage] get_study_images(study_uuid, start_uuid=start_uuid, limit=limit, apply_annotations=apply_annotations)

Get Study Images

First item in response is the next item with uuid greater than start_uuid. start_uuid is part of the response

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_image import BIAImage
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
    study_uuid = 'study_uuid_example' # str | 
    start_uuid = bia_integrator_api.StartUuid() # StartUuid |  (optional)
    limit = 10 # int |  (optional) (default to 10)
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Get Study Images
        api_response = api_instance.get_study_images(study_uuid, start_uuid=start_uuid, limit=limit, apply_annotations=apply_annotations)
        print("The response of PrivateApi->get_study_images:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_study_images: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_uuid** | **str**|  | 
 **start_uuid** | [**StartUuid**](.md)|  | [optional] 
 **limit** | **int**|  | [optional] [default to 10]
 **apply_annotations** | **bool**|  | [optional] [default to False]

### Return type

[**List[BIAImage]**](BIAImage.md)

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

# **get_study_images_by_alias**
> List[BIAImage] get_study_images_by_alias(study_accession, aliases, apply_annotations=apply_annotations)

Get Study Images By Alias

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_image import BIAImage
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
    study_accession = 'study_accession_example' # str | 
    aliases = ['aliases_example'] # List[str] | 
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Get Study Images By Alias
        api_response = api_instance.get_study_images_by_alias(study_accession, aliases, apply_annotations=apply_annotations)
        print("The response of PrivateApi->get_study_images_by_alias:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->get_study_images_by_alias: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_accession** | **str**|  | 
 **aliases** | [**List[str]**](str.md)|  | 
 **apply_annotations** | **bool**|  | [optional] [default to False]

### Return type

[**List[BIAImage]**](BIAImage.md)

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

# **health_check**
> object health_check()

Health Check

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
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

    try:
        # Health Check
        api_response = api_instance.health_check()
        print("The response of PrivateApi->health_check:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->health_check: %s\n" % e)
```



### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **login_for_access_token**
> AuthenticationToken login_for_access_token(username, password, grant_type=grant_type, scope=scope, client_id=client_id, client_secret=client_secret)

Login For Access Token

### Example

```python
import time
import os
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

# **register_user**
> object register_user(body_register_user)

Register User

### Example

```python
import time
import os
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

# **search_collections**
> List[BIACollection] search_collections(name=name, apply_annotations=apply_annotations)

Search Collections

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_collection import BIACollection
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
    name = bia_integrator_api.Name() # Name |  (optional)
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Search Collections
        api_response = api_instance.search_collections(name=name, apply_annotations=apply_annotations)
        print("The response of PrivateApi->search_collections:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->search_collections: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | [**Name**](.md)|  | [optional] 
 **apply_annotations** | **bool**|  | [optional] [default to False]

### Return type

[**List[BIACollection]**](BIACollection.md)

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

# **search_file_references_exact_match**
> List[FileReference] search_file_references_exact_match(search_file_reference_filter, apply_annotations=apply_annotations)

Search File References Exact Match

Exact match search of file references with a specific attribute. Multiple parameters mean AND (as in, p1 AND p2). Items in lists with the `_any` suffix are ORed.  Although `study_uuid` is optional, passing it if known is highly recommended and results in faster queries. Queries time out after 2 seconds, which should be enough for any search filtered by study.  This is likely to change fast, so **named arguments are recommended** in client apps instead of positional if possible to prevent downstream breakage.  `name` and `uri_prefix` queries are case insensitive

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.file_reference import FileReference
from bia_integrator_api.models.search_file_reference_filter import SearchFileReferenceFilter
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
    search_file_reference_filter = bia_integrator_api.SearchFileReferenceFilter() # SearchFileReferenceFilter | 
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Search File References Exact Match
        api_response = api_instance.search_file_references_exact_match(search_file_reference_filter, apply_annotations=apply_annotations)
        print("The response of PrivateApi->search_file_references_exact_match:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->search_file_references_exact_match: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_file_reference_filter** | [**SearchFileReferenceFilter**](SearchFileReferenceFilter.md)|  | 
 **apply_annotations** | **bool**|  | [optional] [default to False]

### Return type

[**List[FileReference]**](FileReference.md)

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

# **search_images_exact_match**
> List[BIAImage] search_images_exact_match(search_image_filter, apply_annotations=apply_annotations)

Search Images Exact Match

Exact match search of images with a specific attribute. Multiple parameters mean AND (as in, p1 AND p2). Items in lists with the `_any` suffix are ORed.  Although `study_uuid` is optional, passing it if known is highly recommended and results in faster queries. Queries time out after 2 seconds, which should be enough for any search filtered by study.  This is likely to change fast, so **named arguments are recommended** in client apps instead of positional if possible to prevent downstream breakage.

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_image import BIAImage
from bia_integrator_api.models.search_image_filter import SearchImageFilter
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
    search_image_filter = bia_integrator_api.SearchImageFilter() # SearchImageFilter | 
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Search Images Exact Match
        api_response = api_instance.search_images_exact_match(search_image_filter, apply_annotations=apply_annotations)
        print("The response of PrivateApi->search_images_exact_match:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->search_images_exact_match: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_image_filter** | [**SearchImageFilter**](SearchImageFilter.md)|  | 
 **apply_annotations** | **bool**|  | [optional] [default to False]

### Return type

[**List[BIAImage]**](BIAImage.md)

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

# **search_studies**
> List[BIAStudy] search_studies(start_uuid=start_uuid, limit=limit, apply_annotations=apply_annotations)

Search Studies

@TODO: Define search criteria for the general case  First item in response is the next item with uuid greater than start_uuid. start_uuid is part of the response

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_study import BIAStudy
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
    start_uuid = bia_integrator_api.StartUuid() # StartUuid |  (optional)
    limit = 10 # int |  (optional) (default to 10)
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Search Studies
        api_response = api_instance.search_studies(start_uuid=start_uuid, limit=limit, apply_annotations=apply_annotations)
        print("The response of PrivateApi->search_studies:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->search_studies: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_uuid** | [**StartUuid**](.md)|  | [optional] 
 **limit** | **int**|  | [optional] [default to 10]
 **apply_annotations** | **bool**|  | [optional] [default to False]

### Return type

[**List[BIAStudy]**](BIAStudy.md)

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

# **search_studies_exact_match**
> List[BIAStudy] search_studies_exact_match(search_study_filter, apply_annotations=apply_annotations)

Search Studies Exact Match

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_study import BIAStudy
from bia_integrator_api.models.search_study_filter import SearchStudyFilter
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
    search_study_filter = bia_integrator_api.SearchStudyFilter() # SearchStudyFilter | 
    apply_annotations = False # bool |  (optional) (default to False)

    try:
        # Search Studies Exact Match
        api_response = api_instance.search_studies_exact_match(search_study_filter, apply_annotations=apply_annotations)
        print("The response of PrivateApi->search_studies_exact_match:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->search_studies_exact_match: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_study_filter** | [**SearchStudyFilter**](SearchStudyFilter.md)|  | 
 **apply_annotations** | **bool**|  | [optional] [default to False]

### Return type

[**List[BIAStudy]**](BIAStudy.md)

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

# **set_image_ome_metadata**
> BIAImageOmeMetadata set_image_ome_metadata(image_uuid, ome_metadata_file)

Set Image Ome Metadata

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_image_ome_metadata import BIAImageOmeMetadata
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
    image_uuid = 'image_uuid_example' # str | 
    ome_metadata_file = None # bytearray | 

    try:
        # Set Image Ome Metadata
        api_response = api_instance.set_image_ome_metadata(image_uuid, ome_metadata_file)
        print("The response of PrivateApi->set_image_ome_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->set_image_ome_metadata: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_uuid** | **str**|  | 
 **ome_metadata_file** | **bytearray**|  | 

### Return type

[**BIAImageOmeMetadata**](BIAImageOmeMetadata.md)

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **study_refresh_counts**
> object study_refresh_counts(study_uuid)

Study Refresh Counts

Recalculate and persist counts for other objects pointing to this study.

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
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
    study_uuid = 'study_uuid_example' # str | 

    try:
        # Study Refresh Counts
        api_response = api_instance.study_refresh_counts(study_uuid)
        print("The response of PrivateApi->study_refresh_counts:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->study_refresh_counts: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_uuid** | **str**|  | 

### Return type

**object**

### Authorization

[OAuth2PasswordBearer](../README.md#OAuth2PasswordBearer)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_biosample**
> object update_biosample(biosample)

Update Biosample

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.biosample import Biosample
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
    biosample = bia_integrator_api.Biosample() # Biosample | 

    try:
        # Update Biosample
        api_response = api_instance.update_biosample(biosample)
        print("The response of PrivateApi->update_biosample:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->update_biosample: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **biosample** | [**Biosample**](Biosample.md)|  | 

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_file_reference**
> object update_file_reference(file_reference)

Update File Reference

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
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
        # Update File Reference
        api_response = api_instance.update_file_reference(file_reference)
        print("The response of PrivateApi->update_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->update_file_reference: %s\n" % e)
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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_image**
> object update_image(bia_image)

Update Image

Bulk update not available - update_many only has one filter for the entire update @TODO: Find common bulk update usecases and map them to mongo operations

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_image import BIAImage
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
    bia_image = bia_integrator_api.BIAImage() # BIAImage | 

    try:
        # Update Image
        api_response = api_instance.update_image(bia_image)
        print("The response of PrivateApi->update_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->update_image: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bia_image** | [**BIAImage**](BIAImage.md)|  | 

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_image_acquisition**
> object update_image_acquisition(image_acquisition)

Update Image Acquisition

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
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
        # Update Image Acquisition
        api_response = api_instance.update_image_acquisition(image_acquisition)
        print("The response of PrivateApi->update_image_acquisition:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->update_image_acquisition: %s\n" % e)
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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_specimen**
> object update_specimen(specimen)

Update Specimen

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
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
        # Update Specimen
        api_response = api_instance.update_specimen(specimen)
        print("The response of PrivateApi->update_specimen:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->update_specimen: %s\n" % e)
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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_study**
> object update_study(bia_study)

Update Study

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_study import BIAStudy
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
    bia_study = bia_integrator_api.BIAStudy() # BIAStudy | 

    try:
        # Update Study
        api_response = api_instance.update_study(bia_study)
        print("The response of PrivateApi->update_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PrivateApi->update_study: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bia_study** | [**BIAStudy**](BIAStudy.md)|  | 

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
**200** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

