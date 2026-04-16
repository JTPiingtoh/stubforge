from inspect import signature
from typing import Callable, Any, TypeAlias, Literal, TypedDict
import json
import inspect

from tools import parse_dict

JSON: TypeAlias = dict | list
typed_sjon: TypeAlias = dict | str

FieldName: TypeAlias = str
FieldType: TypeAlias = str
# The name of a schema
SchemaName: TypeAlias = str

class Field(TypedDict):
    field_name : FieldName
    field_type : FieldType

# The fields and types of a schema, stored in a list
SchemaFields: TypeAlias = list[Field]

# An object that contains the name of the schema, and its fields 
class Schema(TypedDict):
    schema_name: SchemaName
    schema_fields: SchemaFields



schema1 : Schema = {
    "schema_name" : "schema1",
    "schema_fields" : [
        {
            "field_name" : "age",
            "field_type" : "int"
        },
        {
            "field_name" : "height",
            "field_type" : "int"
        },
    ]
}

schema2 : Schema = {
    "schema_name" : "schema2",
    "schema_fields" : [
        {
            "field_name" : "iq",
            "field_type" : "int"
        },
        {
            "field_name" : "alpha",
            "field_type" : "Bool"
        },
    ]
}

schemas_orig = [schema1, schema2]

# with open("test.json", "w+") as f:
#     json.dump(schemas_orig, f)

with open("test.json", "r") as f:
    schemas_new: list[Schema] = json.load(f)
    assert(schemas_new == schemas_orig)
    
    func_file_path = inspect.getfile(parse_dict)
    func_file_name = func_file_path.split("\\")[-1]
    func_base_path = func_file_path.removesuffix(func_file_name)
    print(func_file_name)
    print(func_base_path)

