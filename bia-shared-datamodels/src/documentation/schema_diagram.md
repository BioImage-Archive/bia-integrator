```mermaid
erDiagram
BIARecord {
    string uuid  
}
Document {
    stringList author  
    string title  
    date release_date  
    stringList keywords  
    stringList acknowledgements  
    string description  
}
Study {
    string accession_id  
    integer file_reference_count  
    integer image_count  
    stringList see_also  
    string fundedBy  
    string uuid  
    stringList author  
    string title  
    date release_date  
    stringList keywords  
    stringList acknowledgements  
    string description  
}
Publication {
    uriorcurie pubmed_id  
    uriorcurie doi  
    stringList author  
    string title  
    date release_date  
    stringList keywords  
    stringList acknowledgements  
    string description  
}
StudyComponent {
    string title  
    string description  
}

Study ||--}o StudyComponent : "part"
StudyComponent ||--|| Study : "partOf"

```

