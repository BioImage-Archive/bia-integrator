# bia-shared-datamodels



URI: https://www.ebi.ac.uk/bioimage-archive/schema/

Name: bia-shared-datamodels



## Classes

| Class | Description |
| --- | --- |
| [BIARecord](BIARecord.md) | a individal record stored in the BioImageArchive |
| [Document](Document.md) | A documentary resource or body of scientific work. |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Publication](Publication.md) | None |
| &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[Study](Study.md) | A study in the BioImageArchive represents a set of image data, and the scienfitic effort that resulted in its creation. |
| [StudyComponent](StudyComponent.md) | A StudyComponent is a dataset of images in which the same set of imaging techniques were performed on a set of specimens and biosamples. |



## Slots

| Slot | Description |
| --- | --- |
| [accession_id](accession_id.md) | Unique ID of a study |
| [acknowledgements](acknowledgements.md) | Any people or groups that should be acknowledged as part of the document |
| [author](author.md) | The creators of the document |
| [description](description.md) | Brief description of the scientific document |
| [doi](doi.md) | Digital Object Identifier (DOI) |
| [file_reference_count](file_reference_count.md) | Number of files associated with the study |
| [fundedBy](fundedBy.md) | The grants that funded the study |
| [image_count](image_count.md) | Number of images associated with the study |
| [keywords](keywords.md) | Keywords or tags used to describe the subject of a document |
| [license](license.md) | The license under which the data are available |
| [part](part.md) | A related document that is included logically in the described document |
| [partOf](partOf.md) | A related document in which the described document is logically included |
| [pubmed_id](pubmed_id.md) | Identifier for journal articles/abstracts in PubMed |
| [release_date](release_date.md) | Date of first publication |
| [see_also](see_also.md) | Links to publications, github repositories, and other pages related to this S... |
| [title](title.md) | The title of a scientific document |
| [uuid](uuid.md) | uuid for the record - this can be used to programmatically retreive the recor... |


## Enumerations

| Enumeration | Description |
| --- | --- |
| [LicenseType](LicenseType.md) |  |


## Types

| Type | Description |
| --- | --- |
| [Boolean](Boolean.md) | A binary (true or false) value |
| [Curie](Curie.md) | a compact URI |
| [Date](Date.md) | a date (year, month and day) in an idealized calendar |
| [DateOrDatetime](DateOrDatetime.md) | Either a date or a datetime |
| [Datetime](Datetime.md) | The combination of a date and time |
| [Decimal](Decimal.md) | A real number with arbitrary precision that conforms to the xsd:decimal speci... |
| [Double](Double.md) | A real number that conforms to the xsd:double specification |
| [Float](Float.md) | A real number that conforms to the xsd:float specification |
| [Integer](Integer.md) | An integer |
| [Jsonpath](Jsonpath.md) | A string encoding a JSON Path |
| [Jsonpointer](Jsonpointer.md) | A string encoding a JSON Pointer |
| [Ncname](Ncname.md) | Prefix part of CURIE |
| [Nodeidentifier](Nodeidentifier.md) | A URI, CURIE or BNODE that represents a node in a model |
| [Objectidentifier](Objectidentifier.md) | A URI or CURIE that represents an object in the model |
| [Sparqlpath](Sparqlpath.md) | A string encoding a SPARQL Property Path |
| [String](String.md) | A character string |
| [Time](Time.md) | A time object represents a (local) time of day, independent of any particular... |
| [Uri](Uri.md) | a complete URI |
| [Uriorcurie](Uriorcurie.md) | a URI or a CURIE |


## Subsets

| Subset | Description |
| --- | --- |
