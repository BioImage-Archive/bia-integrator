# bia_integrator_api.PublicApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_collection**](PublicApi.md#get_collection) | **GET** /api/v1/collections/{collection_uuid} | Get Collection
[**get_file_reference**](PublicApi.md#get_file_reference) | **GET** /api/v1/file_references/{file_reference_uuid} | Get File Reference
[**get_image**](PublicApi.md#get_image) | **GET** /api/v1/images/{image_uuid} | Get Image
[**get_object_info_by_accession**](PublicApi.md#get_object_info_by_accession) | **GET** /api/v1/object_info_by_accessions | Get Object Info By Accession
[**get_study**](PublicApi.md#get_study) | **GET** /api/v1/studies/{study_uuid} | Get Study
[**get_study_file_references**](PublicApi.md#get_study_file_references) | **GET** /api/v1/studies/{study_uuid}/file_references | Get Study File References
[**get_study_images**](PublicApi.md#get_study_images) | **GET** /api/v1/studies/{study_uuid}/images | Get Study Images
[**get_study_images_by_alias**](PublicApi.md#get_study_images_by_alias) | **GET** /api/v1/studies/{study_accession}/images_by_aliases | Get Study Images By Alias
[**search_collections**](PublicApi.md#search_collections) | **GET** /api/v1/collections | Search Collections
[**search_images**](PublicApi.md#search_images) | **GET** /api/v1/search/images | Search Images
[**search_studies**](PublicApi.md#search_studies) | **GET** /api/v1/search/studies | Search Studies


# **get_collection**
> BIACollection get_collection(collection_uuid)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    collection_uuid = None # object | 

    try:
        # Get Collection
        api_response = api_instance.get_collection(collection_uuid)
        print("The response of PublicApi->get_collection:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_collection: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **collection_uuid** | [**object**](.md)|  | 

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
    file_reference_uuid = None # object | 

    try:
        # Get File Reference
        api_response = api_instance.get_file_reference(file_reference_uuid)
        print("The response of PublicApi->get_file_reference:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_file_reference: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **file_reference_uuid** | [**object**](.md)|  | 

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
> BIAImageOutput get_image(image_uuid)

Get Image

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_image_output import BIAImageOutput
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
    image_uuid = None # object | 

    try:
        # Get Image
        api_response = api_instance.get_image(image_uuid)
        print("The response of PublicApi->get_image:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **image_uuid** | [**object**](.md)|  | 

### Return type

[**BIAImageOutput**](BIAImageOutput.md)

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
> object get_object_info_by_accession(accessions)

Get Object Info By Accession

### Example

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


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    accessions = None # object | 

    try:
        # Get Object Info By Accession
        api_response = api_instance.get_object_info_by_accession(accessions)
        print("The response of PublicApi->get_object_info_by_accession:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_object_info_by_accession: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **accessions** | [**object**](.md)|  | 

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

# **get_study**
> BIAStudyOutput get_study(study_uuid)

Get Study

### Example

```python
import time
import os
import bia_integrator_api
from bia_integrator_api.models.bia_study_output import BIAStudyOutput
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
    study_uuid = None # object | 

    try:
        # Get Study
        api_response = api_instance.get_study(study_uuid)
        print("The response of PublicApi->get_study:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_study: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_uuid** | [**object**](.md)|  | 

### Return type

[**BIAStudyOutput**](BIAStudyOutput.md)

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
> object get_study_file_references(study_uuid, start_uuid=start_uuid, limit=limit)

Get Study File References

First item in response is the next item with uuid greater than start_uuid. start_uuid is part of the response

### Example

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


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    study_uuid = None # object | 
    start_uuid = None # object |  (optional)
    limit = None # object |  (optional)

    try:
        # Get Study File References
        api_response = api_instance.get_study_file_references(study_uuid, start_uuid=start_uuid, limit=limit)
        print("The response of PublicApi->get_study_file_references:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_study_file_references: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_uuid** | [**object**](.md)|  | 
 **start_uuid** | [**object**](.md)|  | [optional] 
 **limit** | [**object**](.md)|  | [optional] 

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

# **get_study_images**
> object get_study_images(study_uuid, start_uuid=start_uuid, limit=limit)

Get Study Images

First item in response is the next item with uuid greater than start_uuid. start_uuid is part of the response

### Example

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


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    study_uuid = None # object | 
    start_uuid = None # object |  (optional)
    limit = None # object |  (optional)

    try:
        # Get Study Images
        api_response = api_instance.get_study_images(study_uuid, start_uuid=start_uuid, limit=limit)
        print("The response of PublicApi->get_study_images:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_study_images: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_uuid** | [**object**](.md)|  | 
 **start_uuid** | [**object**](.md)|  | [optional] 
 **limit** | [**object**](.md)|  | [optional] 

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

# **get_study_images_by_alias**
> object get_study_images_by_alias(study_accession, aliases)

Get Study Images By Alias

### Example

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


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    study_accession = None # object | 
    aliases = None # object | 

    try:
        # Get Study Images By Alias
        api_response = api_instance.get_study_images_by_alias(study_accession, aliases)
        print("The response of PublicApi->get_study_images_by_alias:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_study_images_by_alias: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **study_accession** | [**object**](.md)|  | 
 **aliases** | [**object**](.md)|  | 

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

# **search_collections**
> object search_collections(name=name)

Search Collections

### Example

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


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    name = None # object |  (optional)

    try:
        # Search Collections
        api_response = api_instance.search_collections(name=name)
        print("The response of PublicApi->search_collections:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_collections: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **name** | [**object**](.md)|  | [optional] 

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

# **search_images**
> object search_images(alias=alias, body=body)

Search Images

### Example

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


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    alias = None # object |  (optional)
    body = bia_integrator_api.BodySearchImages() # BodySearchImages |  (optional)

    try:
        # Search Images
        api_response = api_instance.search_images(alias=alias, body=body)
        print("The response of PublicApi->search_images:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_images: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **alias** | [**object**](.md)|  | [optional] 
 **body** | **BodySearchImages**|  | [optional] 

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

# **search_studies**
> object search_studies(start_uuid=start_uuid, limit=limit)

Search Studies

@TODO: Define search criteria for the general case  First item in response is the next item with uuid greater than start_uuid. start_uuid is part of the response

### Example

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


# Enter a context with an instance of the API client
with bia_integrator_api.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = bia_integrator_api.PublicApi(api_client)
    start_uuid = None # object |  (optional)
    limit = None # object |  (optional)

    try:
        # Search Studies
        api_response = api_instance.search_studies(start_uuid=start_uuid, limit=limit)
        print("The response of PublicApi->search_studies:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_studies: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **start_uuid** | [**object**](.md)|  | [optional] 
 **limit** | [**object**](.md)|  | [optional] 

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

