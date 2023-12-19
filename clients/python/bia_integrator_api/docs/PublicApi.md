# bia_integrator_api.PublicApi

All URIs are relative to *http://localhost*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_collection**](PublicApi.md#get_collection) | **GET** /api/v1/collections/{collection_uuid} | Get Collection
[**get_file_reference**](PublicApi.md#get_file_reference) | **GET** /api/v1/file_references/{file_reference_uuid} | Get File Reference
[**get_image**](PublicApi.md#get_image) | **GET** /api/v1/images/{image_uuid} | Get Image
[**get_image_ome_metadata**](PublicApi.md#get_image_ome_metadata) | **GET** /api/v1/images/{image_uuid}/ome_metadata | Get Image Ome Metadata
[**get_object_info_by_accession**](PublicApi.md#get_object_info_by_accession) | **GET** /api/v1/object_info_by_accessions | Get Object Info By Accession
[**get_study**](PublicApi.md#get_study) | **GET** /api/v1/studies/{study_uuid} | Get Study
[**get_study_file_references**](PublicApi.md#get_study_file_references) | **GET** /api/v1/studies/{study_uuid}/file_references | Get Study File References
[**get_study_images**](PublicApi.md#get_study_images) | **GET** /api/v1/studies/{study_uuid}/images | Get Study Images
[**get_study_images_by_alias**](PublicApi.md#get_study_images_by_alias) | **GET** /api/v1/studies/{study_accession}/images_by_aliases | Get Study Images By Alias
[**search_collections**](PublicApi.md#search_collections) | **GET** /api/v1/collections | Search Collections
[**search_file_references_exact_match**](PublicApi.md#search_file_references_exact_match) | **POST** /api/v1/search/file_references/exact_match | Search File References Exact Match
[**search_images_exact_match**](PublicApi.md#search_images_exact_match) | **POST** /api/v1/search/images/exact_match | Search Images Exact Match
[**search_studies**](PublicApi.md#search_studies) | **GET** /api/v1/search/studies | Search Studies
[**search_studies_exact_match**](PublicApi.md#search_studies_exact_match) | **POST** /api/v1/search/studies/exact_match | Search Studies Exact Match


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
    collection_uuid = 'collection_uuid_example' # str | 

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
    file_reference_uuid = 'file_reference_uuid_example' # str | 

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    image_uuid = 'image_uuid_example' # str | 

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    image_uuid = 'image_uuid_example' # str | 

    try:
        # Get Image Ome Metadata
        api_response = api_instance.get_image_ome_metadata(image_uuid)
        print("The response of PublicApi->get_image_ome_metadata:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->get_image_ome_metadata: %s\n" % e)
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    accessions = ['accessions_example'] # List[str] | 

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    study_uuid = 'study_uuid_example' # str | 

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    study_uuid = 'study_uuid_example' # str | 
    start_uuid = bia_integrator_api.StartUuid() # StartUuid |  (optional)
    limit = 10 # int |  (optional) (default to 10)

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
 **study_uuid** | **str**|  | 
 **start_uuid** | [**StartUuid**](.md)|  | [optional] 
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    study_uuid = 'study_uuid_example' # str | 
    start_uuid = bia_integrator_api.StartUuid() # StartUuid |  (optional)
    limit = 10 # int |  (optional) (default to 10)

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
 **study_uuid** | **str**|  | 
 **start_uuid** | [**StartUuid**](.md)|  | [optional] 
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
    api_instance = bia_integrator_api.PublicApi(api_client)
    study_accession = 'study_accession_example' # str | 
    aliases = ['aliases_example'] # List[str] | 

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

# **search_collections**
> List[BIACollection] search_collections(name=name)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    name = bia_integrator_api.Name() # Name |  (optional)

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
 **name** | [**Name**](.md)|  | [optional] 

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
> List[FileReference] search_file_references_exact_match(search_file_reference_filter)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    search_file_reference_filter = bia_integrator_api.SearchFileReferenceFilter() # SearchFileReferenceFilter | 

    try:
        # Search File References Exact Match
        api_response = api_instance.search_file_references_exact_match(search_file_reference_filter)
        print("The response of PublicApi->search_file_references_exact_match:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_file_references_exact_match: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_file_reference_filter** | [**SearchFileReferenceFilter**](SearchFileReferenceFilter.md)|  | 

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
> List[BIAImage] search_images_exact_match(search_image_filter)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    search_image_filter = bia_integrator_api.SearchImageFilter() # SearchImageFilter | 

    try:
        # Search Images Exact Match
        api_response = api_instance.search_images_exact_match(search_image_filter)
        print("The response of PublicApi->search_images_exact_match:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_images_exact_match: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_image_filter** | [**SearchImageFilter**](SearchImageFilter.md)|  | 

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    start_uuid = bia_integrator_api.StartUuid() # StartUuid |  (optional)
    limit = 10 # int |  (optional) (default to 10)

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
 **start_uuid** | [**StartUuid**](.md)|  | [optional] 
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

# **search_studies_exact_match**
> List[BIAStudy] search_studies_exact_match(search_study_filter)

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
    api_instance = bia_integrator_api.PublicApi(api_client)
    search_study_filter = bia_integrator_api.SearchStudyFilter() # SearchStudyFilter | 

    try:
        # Search Studies Exact Match
        api_response = api_instance.search_studies_exact_match(search_study_filter)
        print("The response of PublicApi->search_studies_exact_match:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling PublicApi->search_studies_exact_match: %s\n" % e)
```



### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **search_study_filter** | [**SearchStudyFilter**](SearchStudyFilter.md)|  | 

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

