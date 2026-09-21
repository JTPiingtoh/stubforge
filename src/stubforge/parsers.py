from inspect import signature
from typing import Callable, Any, TypeAlias, Literal, TypedDict, assert_type
import inspect
import json

from collections import OrderedDict
from stubforge.dict_extras import ordered_dict_updated
from stubforge.namespace import render_new_stub_schema
from stubforge.stubforge_types import *



# Source - https://stackoverflow.com/a/60978847
# Posted by JoshDaBosh, modified by community. See post 'Timeline' for change history
# Retrieved 2026-04-25, License - CC BY-SA 4.0
def to_camel_case(text):
        s = text.replace("-", " ").replace("_", " ")
        s = s.split()
        if len(text) == 0:
            return text
        return s[0] + ''.join(i.capitalize() for i in s[1:])


def _update_schema_list_from_list(
    value: list, 
    schema_list: list[Schema], 
    schema_name: SchemaName) -> list[Schema]:

    type_names_in_list = []
    sub_dtos: int = 0
    for i, obj in enumerate(value):
        type_name: str
        if isinstance(obj, dict):
            # BUG: dict is inheriting the name of the list
            updated_schema_list = _update_schema_list_from_dict(obj, schema_list, schema_name + f"_dto_{sub_dtos}")
            # schema_list[-1]["schema_name"] += f"_{i}"
            sub_dtos+=1
            type_name = updated_schema_list[-1]["schema_name"] 
        else:
            type_name = type(obj).__name__   

        type_names_in_list.append(type_name)

    # This could be made into a seperate function
    if len(type_names_in_list) == 0:
        mutable_field_type.set_string(f"list[{type_names_in_list[0]}]")
    elif all(t == type_names_in_list[0] for t in type_names_in_list):
        mutable_field_type.set_string(f"list[{type_names_in_list[0]}]")
    else:
        unique_types_names = list(set(type_names_in_list))
        unique_types_names.sort()
        mutable_field_type.set_string(f"list[{" | ".join( unique_types_names )}]")


def _update_schema_list_from_dict(
    Dict: dict, 
    schema_list: list[Schema], 
    schema_name: SchemaName) -> list[Schema]:

    if not isinstance(Dict, dict) or Dict.keys() in [
        fields.keys() for fields in [
            schema["schema_fields_dict"] for schema in schema_list
            ]
        ]:
        return schema_list

    # build a list containing names and types of this dict
    schema_fields_dict: OrderedDict[SchemaName, SchemaFieldType] = OrderedDict()
    updated_schema_list: list[Schema] = []

    for key, value in Dict.items():

        field_name: SchemaFieldName = str(key)
        schema_field_type: SchemaFieldType

        if isinstance(value, dict):
            updated_schema_list = _update_schema_list_from_dict(value, schema_list, to_camel_case(key) + "_dto")
            # a new schema has been added to the list. The name of this schema is the field type of Dict[key]
            schema_field_type = updated_schema_list[-1]["schema_name"]

        elif isinstance(value, list):
            updated_schema_list = _update_schema_list_from_list(value, schema_list, to_camel_case(key) + "_dto")

        else:
            schema_field_type = type(value).__name__

        schema_fields_dict[field_name] = schema_field_type

    # schema_name += "_dto"
    updated_schema_list.append({"schema_name" : f"{schema_name}", "schema_fields_dict" : schema_fields_dict})
    

    return updated_schema_list
    

def render_schema_list(object: Any, object_name: SchemaName) -> tuple[SchemaName, list[Schema]]:

    schema_list: list[Schema] = []
    schema_name: SchemaName = ""

    if isinstance(object, dict):
        schema_list = _update_schema_list_from_dict(object, schema_list, object_name  + "_dto")
        schema_name = schema_list[-1]["schema_name"]

    elif isinstance(object, list):

        schema_list = _update_schema_list_from_list(object, schema_list, object_name  + "_dto")

    return schema_list
    