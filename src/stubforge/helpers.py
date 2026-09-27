from stubforge.stubforge_types import *

def dict_in_schema_list(dict_object: dict, schema_list: list[Schema]) -> bool:
    
    return dict_object.keys() in [
        schema_fields_dict.keys() for schema_fields_dict in [
            schema["schema_fields_dict"] for schema in schema_list
            ]
        ]

def retrieve_schema_name_from_schema_list(dict_object: dict, schema_list: list[Schema]) -> SchemaName | None:
 
    for schema in schema_list:
        if dict_object.keys() in [schema["schema_fields_dict"].keys()]:
            return schema["schema_name"]

    return None

# Source - https://stackoverflow.com/a/60978847
# Posted by JoshDaBosh, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-25, License - CC BY-SA 4.0
def to_camel_case(text: str) -> str:
        s = text.replace("-", " ").replace("_", " ")
        s = s.split()
        if len(text) == 0:
            return text
        return s[0] + ''.join(i.capitalize() for i in s[1:])