fields_map = {
    "study": {
        "facet.organism": "organism_scientific_name.keyword",
        "facet.imaging_method": "imaging_method.keyword",
        "facet.year": "release_date",
        "facet.licence": "licence",
        "facet.annotation_method": "annotation_type.keyword",
        "has":
         {"thumbnail": "example_image"}
    },
    "image": {
        "facet.organism": "organism_scientific_name.keyword",
        "facet.imaging_method": "imaging_method.keyword",
        "facet.annotation_method": "annotation_type.keyword",
        "facet.image_format": "representation.image_format",
        "numeric": {
            "size_x": "representation.size_x",
            "size_y": "representation.size_y",
            "size_z": "representation.size_z",
            "size_c": "representation.size_c",
            "size_t": "representation.size_t",
            "total_size_in_bytes": "representation.total_size_in_bytes",
            "voxel_physical_size_x": "representation.voxel_physical_size_x",
            "voxel_physical_size_y": "representation.voxel_physical_size_y",
            "voxel_physical_size_z": "representation.voxel_physical_size_z",
            "total_physical_size_x": "total_physical_size_x",
            "total_physical_size_y": "total_physical_size_y",
            "total_physical_size_z": "total_physical_size_z",
        }
    },
    
}

operators_map = {
    "numeric": {
        "eq": "",
        "gt": "gt",
        "gte": "gte",
        "lt": "lt",
        "lte": "lte",
        "or": "or",
        "not": "not"
    },
    "boolean_operators": {"and", "or", "not"}}

aggregations = {
    "study": {
        "scientific_name": { "terms": {"field": fields_map["study"]["facet.organism"] }},
        "release_date": {
            "date_histogram": {
                "field": fields_map["study"]["facet.year"],
                "calendar_interval": "1y",
                "format": "yyyy",
            }
        },
        "imaging_method": { "terms": {"field": f"{fields_map["study"]["facet.imaging_method"]}" }},
        "annotation_method": { "terms": {"field": fields_map["study"]["facet.annotation_method"] }},
        "licence": { "terms": {"field": fields_map["study"]["facet.licence"] }},
    }, 
    "image" : {
        "scientific_name": { "terms": {"field": fields_map["image"]["facet.organism"] }},
        "image_format": { "terms": {"field": fields_map["image"]["facet.image_format"] }},
        "imaging_method": { "terms": {"field": fields_map["image"]["facet.imaging_method"]}},
        "annotation_method": { "terms": {"field": fields_map["image"]["facet.annotation_method"]}},
        "number_of_channels": {
            "filters": {
                "keyed": False,
                "filters": {
                    "1":  { "term":  { fields_map["image"]["numeric"]["size_c"]: 1 } }, "2":  { "term":  { fields_map["image"]["numeric"]["size_c"]: 2 } }, 
                    "3":  { "term":  { fields_map["image"]["numeric"]["size_c"]: 3 } }, "4":  { "term":  { fields_map["image"]["numeric"]["size_c"]: 4 } }, 
                    "5":  { "term":  { fields_map["image"]["numeric"]["size_c"]: 5 } }, "More than 5": { "range": { fields_map["image"]["numeric"]["size_c"]: { "gt": 5 } } }
                }
            }
        }
    }
}

numeric_aggs = {
    "image_pixel_x": fields_map["image"]["numeric"]["size_x"],
    "image_pixel_y": fields_map["image"]["numeric"]["size_y"],
    "z_planes": fields_map["image"]["numeric"]["size_z"],
    "time_steps": fields_map["image"]["numeric"]["size_t"],
    "total_size_in_bytes": fields_map["image"]["numeric"]["total_size_in_bytes"],
    "total_physical_size_x": fields_map["image"]["numeric"]["total_physical_size_x"],
    "total_physical_size_y": fields_map["image"]["numeric"]["total_physical_size_y"],
    "total_physical_size_z": fields_map["image"]["numeric"]["total_physical_size_z"],
    "voxel_physical_size_x": fields_map["image"]["numeric"]["voxel_physical_size_x"],
    "voxel_physical_size_y": fields_map["image"]["numeric"]["voxel_physical_size_y"],
    "voxel_physical_size_z": fields_map["image"]["numeric"]["voxel_physical_size_z"],
}

aggregations["image"]["selected"] = {
    "filter": {"match_all": {}},
    "aggs": {k: {"stats": {"field": f}} for k, f in numeric_aggs.items()},
}

aggregations["image"]["all_stats"] = {
    "global": {},
    "aggs": {k: {"stats": {"field": f}} for k, f in numeric_aggs.items()},
}

study_browse_card_field_l = ["uuid", "accession_id", "title", "description", "release_date", " licence", "keyword", "imaging_method", "annotation_type", "image_format", "organism_scientific_name", "organism_common_name", "example_image"]
image_browse_card_field_l = ["uuid", "accession_id", "title", "description", "release_date", " licence", "additional_metadata", "total_physical_size_x", "total_physical_size_y", "total_physical_size_z", "imaging_method", "annotation_type", "organism_scientific_name", "organism_common_name", "representation"]
