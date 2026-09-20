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


def parse_object_if_list(
    value: list, 
    schema_list: list[Schema], 
    object_name: ObjectName,  
    mutable_field_type: MutableString) -> tuple[SchemaName, list[Schema]]:

    type_names_in_list = []
    sub_dtos: int = 0
    for i, obj in enumerate(value):
        type_name: str
        if isinstance(obj, dict):
            # BUG: dict is inheriting the name of the list
            schema_name, schema_list = parse_object_if_dict(obj, schema_list, schema_name + f"_dto_{sub_dtos}")
            # schema_list[-1]["schema_name"] += f"_{i}"
            sub_dtos+=1
            type_name = schema_list[-1]["schema_name"] 
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


def parse_object_if_dict(
    result: dict, 
    schema_list: list[Schema], 
    object_name: ObjectName) -> tuple[SchemaName, list[Schema]]:

    schema_name: SchemaName

    if not isinstance(result, dict) or result.keys() in [
        fields.keys() for fields in [
            schema["schema_fields"] for schema in schema_list
            ]
        ]:
        return object_name, schema_list

    # build a list containing names and types of this dict
    schema_fields_dict: SchemaFieldsDict = OrderedDict()
    new_schema_list: list[Schema] = []

    for key, value in result.items():

        field_name: SchemaName = str(key)
        field_type: FieldType

        if isinstance(value, dict):
            field_name, new_schema_list = parse_object_if_dict(value, schema_list, to_camel_case(key) + "_dto")
            # field_type = new_schema_list[-1]["schema_name"]

        elif isinstance(value, list):
            field_name, new_schema_list = parse_object_if_list(value, schema_list, to_camel_case(key) + "_dto")

        else:
            field_name = type(value).__name__

        schema_fields_dict[field_name] = field_name

    # schema_name += "_dto"
    new_schema_list.append({"schema_name" : f"{object_name}", "schema_fields" : schema_fields_dict})
    schema_name = new_schema_list[-1]["schema_name"]

    return schema_name, new_schema_list
    

def parse_object(object: Any, object_name: ObjectName) -> tuple[SchemaName, list[Schema]]:

    schema_list: list[Schema] = []
    schema_name: SchemaName = ""

    if isinstance(object, dict):
        schema_list = parse_object_if_dict(object, schema_list, object_name  + "_dto")
        schema_name = schema_list[-1]["schema_name"]

    elif isinstance(object, list):

        mutable_schema_name = MutableString("")
        schema_list = parse_object_if_list(object, schema_list, object_name + "_dto", mutable_schema_name)
        schema_name = ""

    return schema_name, schema_list
    