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


def parse_list(value: list, schema_list: list[Schema], schema_name: str, func_name: str, mutable_field_type: MutableString):

    type_names_in_list = []
    for obj in value:
        type_name: str
        if isinstance(obj, dict):
            parse_dict(obj, schema_list, schema_name, func_name)
            type_name = schema_list[-1]["schema_name"]
        else:
            type_name = type(obj).__name__   
        type_names_in_list.append(type_name)

    if len(type_names_in_list) == 0:
        mutable_field_type.set_string(f"list[{type_names_in_list[0]}]")
    elif all(t == type_names_in_list[0] for t in type_names_in_list):
        mutable_field_type.set_string(f"list[{type_names_in_list[0]}]")
    else:
        mutable_field_type.set_string(f"list[{" | ".join( list(set(type_names_in_list)) )}]")


def parse_dict(result: dict, schema_list: list[Schema], schema_name: str, func_name: str):

    if not isinstance(result, dict) or result.keys() in [fields.keys() for fields in [schema["schema_fields"] for schema in schema_list]]:
        return

    # build a list containing names and types of this dict
    schema_fields: SchemaFields = OrderedDict()
    for key, value in result.items():

        field_name: FieldName = str(key)
        field_type: FieldType

        if isinstance(value, dict):
            parse_dict(value, schema_list, to_camel_case(key), func_name)
            field_type = schema_list[-1]["schema_name"]

        elif isinstance(value, list):
            mutable_field_type = MutableString("")
            parse_list(value, schema_list, to_camel_case(key), func_name, mutable_field_type)
            field_type = mutable_field_type.get_string()

        else:
            field_type = type(value).__name__

        schema_fields[field_name] = field_type
    

    schema_name += "_dto"
    schema_list.append({"schema_name" : f"{schema_name}", "schema_fields" : schema_fields})

    return