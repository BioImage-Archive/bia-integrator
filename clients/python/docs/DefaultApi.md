# openapi_client.DefaultApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_collection**](DefaultApi.md#create_collection) | **POST** /api/private/collections | Create Collection
[**create_file_reference**](DefaultApi.md#create_file_reference) | **POST** /api/private/file_references | Create File Reference
[**create_image_representation**](DefaultApi.md#create_image_representation) | **POST** /api/private/images/{image_uuid}/representations/single | Create Image Representation
[**create_images**](DefaultApi.md#create_images) | **POST** /api/private/images | Create Images
[**create_images_bulk**](DefaultApi.md#create_images_bulk) | **POST** /api/private/images/bulk | Create Images Bulk
[**create_study**](DefaultApi.md#create_study) | **POST** /api/private/study | Create Study
[**get_collection**](DefaultApi.md#get_collection) | **GET** /api/collections/{collection_uuid} | Get Collection
[**get_file_reference**](DefaultApi.md#get_file_reference) | **GET** /api/file_references/{file_reference_uuid} | Get File Reference
[**get_image**](DefaultApi.md#get_image) | **GET** /api/images/{image_uuid} | Get Image
[**get_image_ome_metadata**](DefaultApi.md#get_image_ome_metadata) | **GET** /api/images/{image_uuid}/ome_metadata | Get Image Ome Metadata
[**get_object_info_by_accession**](DefaultApi.md#get_object_info_by_accession) | **GET** /api/object_info_by_accessions | Get Object Info By Accession
[**get_study**](DefaultApi.md#get_study) | **GET** /api/studies/{study_uuid} | Get Study
[**get_study_file_references**](DefaultApi.md#get_study_file_references) | **GET** /api/studies/{study_uuid}/file_references | Get Study File References
[**get_study_images**](DefaultApi.md#get_study_images) | **GET** /api/studies/{study_uuid}/images | Get Study Images
[**get_study_images_by_alias**](DefaultApi.md#get_study_images_by_alias) | **GET** /api/studies/{study_accession}/images_by_aliases | Get Study Images By Alias
[**health_check**](DefaultApi.md#health_check) | **GET** /admin/health-check | Health Check
[**login_for_access_token**](DefaultApi.md#login_for_access_token) | **POST** /auth/token | Login For Access Token
[**register_user**](DefaultApi.md#register_user) | **GET** /auth/users/register | Register User
[**search_collections**](DefaultApi.md#search_collections) | **GET** /api/collections | Search Collections
[**search_images**](DefaultApi.md#search_images) | **GET** /api/search/images | Search Images
[**search_studies**](DefaultApi.md#search_studies) | **GET** /api/search/studies | Search Studies
[**study_refresh_counts**](DefaultApi.md#study_refresh_counts) | **POST** /api/private/studies/{study_uuid}/refresh_counts | Study Refresh Counts
[**update_file_reference**](DefaultApi.md#update_file_reference) | **PATCH** /api/private/file_references/single | Update File Reference
[**update_image**](DefaultApi.md#update_image) | **PATCH** /api/private/images/single | Update Image
[**update_study**](DefaultApi.md#update_study) | **PATCH** /api/private/study | Update Study


# **create_collection**
> object create_collection(bia_collection)

Create Collection

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import openapi_client
from openapi_client.models.bia_collection import BIACollection
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    bia_collection = openapi_client.BIACollection() # BIACollection | 

    try:
        # Create Collection
        api_response = api_instance.create_collection(bia_collection)
        print("The response of DefaultApi->create_collection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_collection: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bia_collection** | [**BIACollection**](BIACollection.md)|  | 

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

# **create_file_reference**
> BulkOperationResponse create_file_reference(file_reference)

Create File Reference

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import openapi_client
from openapi_client.models.bulk_operation_response import BulkOperationResponse
from openapi_client.models.file_reference import FileReference
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    file_reference = [openapi_client.FileReference()] # List[FileReference] | 

    try:
        # Create File Reference
        api_response = api_instance.create_file_reference(file_reference)
        print("The response of DefaultApi->create_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_file_reference: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_reference** | [**List[FileReference]**](FileReference.md)|  | 

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

# **create_image_representation**
> object create_image_representation(image_uuid, bia_image_representation)

Create Image Representation

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import openapi_client
from openapi_client.models.bia_image_representation import BIAImageRepresentation
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    image_uuid = 'image_uuid_example' # str | 
    bia_image_representation = openapi_client.BIAImageRepresentation() # BIAImageRepresentation | 

    try:
        # Create Image Representation
        api_response = api_instance.create_image_representation(image_uuid, bia_image_representation)
        print("The response of DefaultApi->create_image_representation:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_image_representation: %s\n" % e)
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
> BulkOperationResponse create_images(bia_image)

Create Images

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import openapi_client
from openapi_client.models.bia_image import BIAImage
from openapi_client.models.bulk_operation_response import BulkOperationResponse
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    bia_image = [openapi_client.BIAImage()] # List[BIAImage] | 

    try:
        # Create Images
        api_response = api_instance.create_images(bia_image)
        print("The response of DefaultApi->create_images:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_images: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **bia_image** | [**List[BIAImage]**](BIAImage.md)|  | 

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
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)

    try:
        # Create Images Bulk
        api_response = api_instance.create_images_bulk()
        print("The response of DefaultApi->create_images_bulk:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_images_bulk: %s\n" % e)
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

# **create_study**
> object create_study(bia_study)

Create Study

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import openapi_client
from openapi_client.models.bia_study import BIAStudy
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    bia_study = openapi_client.BIAStudy() # BIAStudy | 

    try:
        # Create Study
        api_response = api_instance.create_study(bia_study)
        print("The response of DefaultApi->create_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->create_study: %s\n" % e)
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
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_collection**
> BIACollection get_collection(collection_uuid)

Get Collection

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.bia_collection import BIACollection
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    collection_uuid = 'collection_uuid_example' # str | 

    try:
        # Get Collection
        api_response = api_instance.get_collection(collection_uuid)
        print("The response of DefaultApi->get_collection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_collection: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_uuid** | **str**|  | 

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
> FileReference get_file_reference(file_reference_uuid)

Get File Reference

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.file_reference import FileReference
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    file_reference_uuid = 'file_reference_uuid_example' # str | 

    try:
        # Get File Reference
        api_response = api_instance.get_file_reference(file_reference_uuid)
        print("The response of DefaultApi->get_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_file_reference: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_reference_uuid** | **str**|  | 

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
> BIAImage get_image(image_uuid)

Get Image

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.bia_image import BIAImage
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    image_uuid = 'image_uuid_example' # str | 

    try:
        # Get Image
        api_response = api_instance.get_image(image_uuid)
        print("The response of DefaultApi->get_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_image: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_uuid** | **str**|  | 

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

# **get_image_ome_metadata**
> object get_image_ome_metadata(image_uuid, study_uuid)

Get Image Ome Metadata

### Example

```python
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    image_uuid = 'image_uuid_example' # str | 
    study_uuid = 'study_uuid_example' # str | 

    try:
        # Get Image Ome Metadata
        api_response = api_instance.get_image_ome_metadata(image_uuid, study_uuid)
        print("The response of DefaultApi->get_image_ome_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_image_ome_metadata: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_uuid** | **str**|  | 
 **study_uuid** | **str**|  | 

### Return type

**object**

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
import openapi_client
from openapi_client.models.object_info import ObjectInfo
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    accessions = ['accessions_example'] # List[str] | 

    try:
        # Get Object Info By Accession
        api_response = api_instance.get_object_info_by_accession(accessions)
        print("The response of DefaultApi->get_object_info_by_accession:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_object_info_by_accession: %s\n" % e)
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

# **get_study**
> BIAStudy get_study(study_uuid)

Get Study

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.bia_study import BIAStudy
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    study_uuid = 'study_uuid_example' # str | 

    try:
        # Get Study
        api_response = api_instance.get_study(study_uuid)
        print("The response of DefaultApi->get_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_study: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_uuid** | **str**|  | 

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
> List[FileReference] get_study_file_references(study_uuid, start_uuid=start_uuid, limit=limit)

Get Study File References

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.file_reference import FileReference
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    study_uuid = 'study_uuid_example' # str | 
    start_uuid = 'start_uuid_example' # str |  (optional)
    limit = 10 # int |  (optional) (default to 10)

    try:
        # Get Study File References
        api_response = api_instance.get_study_file_references(study_uuid, start_uuid=start_uuid, limit=limit)
        print("The response of DefaultApi->get_study_file_references:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_study_file_references: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_uuid** | **str**|  | 
 **start_uuid** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 10]

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
> List[BIAImage] get_study_images(study_uuid, start_uuid=start_uuid, limit=limit)

Get Study Images

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.bia_image import BIAImage
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    study_uuid = 'study_uuid_example' # str | 
    start_uuid = 'start_uuid_example' # str |  (optional)
    limit = 10 # int |  (optional) (default to 10)

    try:
        # Get Study Images
        api_response = api_instance.get_study_images(study_uuid, start_uuid=start_uuid, limit=limit)
        print("The response of DefaultApi->get_study_images:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_study_images: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_uuid** | **str**|  | 
 **start_uuid** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 10]

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
> List[BIAImage] get_study_images_by_alias(study_accession, aliases)

Get Study Images By Alias

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.bia_image import BIAImage
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    study_accession = 'study_accession_example' # str | 
    aliases = ['aliases_example'] # List[str] | 

    try:
        # Get Study Images By Alias
        api_response = api_instance.get_study_images_by_alias(study_accession, aliases)
        print("The response of DefaultApi->get_study_images_by_alias:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->get_study_images_by_alias: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_accession** | **str**|  | 
 **aliases** | [**List[str]**](str.md)|  | 

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

```python
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)

    try:
        # Health Check
        api_response = api_instance.health_check()
        print("The response of DefaultApi->health_check:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->health_check: %s\n" % e)
```


### Parameters
This endpoint does not need any parameter.

### Return type

**object**

### Authorization

No authorization required

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
import openapi_client
from openapi_client.models.authentication_token import AuthenticationToken
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    username = 'username_example' # str | 
    password = 'password_example' # str | 
    grant_type = 'grant_type_example' # str |  (optional)
    scope = '' # str |  (optional) (default to '')
    client_id = 'client_id_example' # str |  (optional)
    client_secret = 'client_secret_example' # str |  (optional)

    try:
        # Login For Access Token
        api_response = api_instance.login_for_access_token(username, password, grant_type=grant_type, scope=scope, client_id=client_id, client_secret=client_secret)
        print("The response of DefaultApi->login_for_access_token:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->login_for_access_token: %s\n" % e)
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
> User register_user(email, password_plain, secret_token)

Register User

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.user import User
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    email = 'email_example' # str | 
    password_plain = 'password_plain_example' # str | 
    secret_token = 'secret_token_example' # str | 

    try:
        # Register User
        api_response = api_instance.register_user(email, password_plain, secret_token)
        print("The response of DefaultApi->register_user:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->register_user: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **email** | **str**|  | 
 **password_plain** | **str**|  | 
 **secret_token** | **str**|  | 

### Return type

[**User**](User.md)

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

# **search_collections**
> List[BIACollection] search_collections(name=name)

Search Collections

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.bia_collection import BIACollection
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    name = 'name_example' # str |  (optional)

    try:
        # Search Collections
        api_response = api_instance.search_collections(name=name)
        print("The response of DefaultApi->search_collections:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->search_collections: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | **str**|  | [optional] 

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

# **search_images**
> List[BIAImage] search_images(alias=alias, body_search_images_api_search_images_get=body_search_images_api_search_images_get)

Search Images

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.bia_image import BIAImage
from openapi_client.models.body_search_images_api_search_images_get import BodySearchImagesApiSearchImagesGet
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    alias = 'alias_example' # str |  (optional)
    body_search_images_api_search_images_get = openapi_client.BodySearchImagesApiSearchImagesGet() # BodySearchImagesApiSearchImagesGet |  (optional)

    try:
        # Search Images
        api_response = api_instance.search_images(alias=alias, body_search_images_api_search_images_get=body_search_images_api_search_images_get)
        print("The response of DefaultApi->search_images:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->search_images: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **alias** | **str**|  | [optional] 
 **body_search_images_api_search_images_get** | [**BodySearchImagesApiSearchImagesGet**](BodySearchImagesApiSearchImagesGet.md)|  | [optional] 

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
> List[BIAStudy] search_studies(start_uuid=start_uuid, limit=limit)

Search Studies

@TODO: Define search criteria for the general case

### Example

```python
import time
import os
import openapi_client
from openapi_client.models.bia_study import BIAStudy
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)


# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    start_uuid = 'start_uuid_example' # str |  (optional)
    limit = 10 # int |  (optional) (default to 10)

    try:
        # Search Studies
        api_response = api_instance.search_studies(start_uuid=start_uuid, limit=limit)
        print("The response of DefaultApi->search_studies:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->search_studies: %s\n" % e)
```


### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_uuid** | **str**|  | [optional] 
 **limit** | **int**|  | [optional] [default to 10]

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

# **study_refresh_counts**
> object study_refresh_counts(study_uuid)

Study Refresh Counts

Recalculate and persist counts for other objects pointing to this study.

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import openapi_client
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    study_uuid = 'study_uuid_example' # str | 

    try:
        # Study Refresh Counts
        api_response = api_instance.study_refresh_counts(study_uuid)
        print("The response of DefaultApi->study_refresh_counts:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->study_refresh_counts: %s\n" % e)
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

# **update_file_reference**
> object update_file_reference(file_reference)

Update File Reference

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import openapi_client
from openapi_client.models.file_reference import FileReference
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    file_reference = openapi_client.FileReference() # FileReference | 

    try:
        # Update File Reference
        api_response = api_instance.update_file_reference(file_reference)
        print("The response of DefaultApi->update_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->update_file_reference: %s\n" % e)
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
import openapi_client
from openapi_client.models.bia_image import BIAImage
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    bia_image = openapi_client.BIAImage() # BIAImage | 

    try:
        # Update Image
        api_response = api_instance.update_image(bia_image)
        print("The response of DefaultApi->update_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->update_image: %s\n" % e)
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

# **update_study**
> object update_study(bia_study)

Update Study

### Example

* OAuth Authentication (OAuth2PasswordBearer):
```python
import time
import os
import openapi_client
from openapi_client.models.bia_study import BIAStudy
from openapi_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = openapi_client.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

configuration.access_token = os.environ["ACCESS_TOKEN"]

# Enter a context with an instance of the API client
with openapi_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = openapi_client.DefaultApi(api_client)
    bia_study = openapi_client.BIAStudy() # BIAStudy | 

    try:
        # Update Study
        api_response = api_instance.update_study(bia_study)
        print("The response of DefaultApi->update_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling DefaultApi->update_study: %s\n" % e)
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
**201** | Successful Response |  -  |
**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)
