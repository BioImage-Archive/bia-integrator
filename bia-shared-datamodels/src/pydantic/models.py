from __future__ import annotations 
from datetime import (
    datetime,
    date
)
from decimal import Decimal 
from enum import Enum 
import re
import sys
from typing import (
    Any,
    List,
    Literal,
    Dict,
    Optional,
    Union
)
from pydantic.version import VERSION  as PYDANTIC_VERSION 
if int(PYDANTIC_VERSION[0])>=2:
    from pydantic import (
        BaseModel,
        ConfigDict,
        Field,
        field_validator
    )
else:
    from pydantic import (
        BaseModel,
        Field,
        validator
    )

metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass


class LicenseType(str, Enum):
    # No Copyright. You can copy, modify, distribute and perform the work, even for commercial purposes, all without asking permission.
    CC0 = "CC0"
    # You are free to: Share — copy and redistribute the material in any medium or format. Adapt — remix, transform, and build upon the material  for any purpose, even commercially. You must give appropriate credit, provide a link to the license, and indicate if changes were made.  You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
    CC_BY = "CC_BY"


class BIARecord(ConfiguredBaseModel):
    """
    a individal record stored in the BioImageArchive
    """
    uuid: str = Field(..., description="""uuid for the record - this can be used to programmatically retreive the record from the BIA API""")


class Document(ConfiguredBaseModel):
    """
    A documentary resource or body of scientific work.
    """
    author: List[str] = Field(default_factory=list, description="""The creators of the document.""")
    title: str = Field(..., description="""The title of a scientific document. This will usually be displayed when search results including your data are shown.""")
    release_date: Optional[date] = Field(None, description="""Date of first publication""")
    keywords: Optional[List[str]] = Field(default_factory=list, description="""Keywords or tags used to describe the subject of a document""")
    acknowledgements: Optional[List[str]] = Field(default_factory=list, description="""Any people or groups that should be acknowledged as part of the document.""")
    description: Optional[str] = Field(None, description="""Brief description of the scientific document.""")


class Study(Document, BIARecord):
    """
    A study in the BioImageArchive represents a set of image data, and the scienfitic effort that resulted in its creation.
    """
    accession_id: str = Field(..., description="""Unique ID of a study""")
    file_reference_count: Optional[int] = Field(None, description="""Number of files associated with the study""")
    image_count: Optional[int] = Field(None, description="""Number of images associated with the study""")
    see_also: Optional[List[str]] = Field(default_factory=list, description="""Links to publications, github repositories, and other pages related to this Study.""")
    fundedBy: Optional[str] = Field(None, description="""The grants that funded the study""")
    part: Optional[List[StudyComponent]] = Field(default_factory=list, description="""A related document that is included logically in the described document.""")
    uuid: str = Field(..., description="""uuid for the record - this can be used to programmatically retreive the record from the BIA API""")
    author: List[str] = Field(default_factory=list, description="""The creators of the document.""")
    title: str = Field(..., description="""The title of a scientific document. This will usually be displayed when search results including your data are shown.""")
    release_date: Optional[date] = Field(None, description="""Date of first publication""")
    keywords: Optional[List[str]] = Field(default_factory=list, description="""Keywords or tags used to describe the subject of a document""")
    acknowledgements: Optional[List[str]] = Field(default_factory=list, description="""Any people or groups that should be acknowledged as part of the document.""")
    description: str = Field(..., description="""Brief description of the scientific document.""")


class Publication(Document):
    pubmed_id: Optional[str] = Field(None, description="""Identifier for journal articles/abstracts in PubMed""")
    doi: str = Field(..., description="""Digital Object Identifier (DOI)""")
    author: List[str] = Field(default_factory=list, description="""The creators of the document.""")
    title: str = Field(..., description="""The title of a scientific document. This will usually be displayed when search results including your data are shown.""")
    release_date: Optional[date] = Field(None, description="""Date of first publication""")
    keywords: Optional[List[str]] = Field(default_factory=list, description="""Keywords or tags used to describe the subject of a document""")
    acknowledgements: Optional[List[str]] = Field(default_factory=list, description="""Any people or groups that should be acknowledged as part of the document.""")
    description: Optional[str] = Field(None, description="""Brief description of the scientific document.""")


class StudyComponent(ConfiguredBaseModel):
    """
    A StudyComponent is a dataset of images in which the same set of imaging techniques were performed on a set of specimens and biosamples.
    """
    title: Optional[str] = Field(None, description="""The title of a scientific document. This will usually be displayed when search results including your data are shown.""")
    description: Optional[str] = Field(None, description="""Brief description of the scientific document.""")
    partOf: str = Field(..., description="""A related document in which the described document is logically included.""")


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
BIARecord.model_rebuild()
Document.model_rebuild()
Study.model_rebuild()
Publication.model_rebuild()
StudyComponent.model_rebuild()

