from stubforge.stubforge_types import *

def dict_in_schema_list(dict_object: dict, schema_list: list[Schema]) -> bool:
    
    return dict_object.keys() in [
        schema_fields_dict.keys() for schema_fields_dict in [
            schema["schema_fields_dict"] for schema in schema_list
            ]
        ]

