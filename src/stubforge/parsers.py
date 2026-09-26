from inspect import signature
from typing import Callable, Any, TypeAlias, Literal, TypedDict, assert_type
import inspect
import json

from dataclasses import dataclass
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

'''
freeChampionIdsForNewPlayers_dto: TypeAlias = list[freeChampionIdsForNewPlayers_0_dto | freeChampionIdsForNewPlayers_1_dto | int]

details_dto = TypedDict("detail_dto", {
   "name" : str,
   "age" : int,
   "active" : bool,
   "score" : float,
})


test_dto = TypedDict("test_dto", {
   "freeChampionIdsForNewPlayers" : freeChampionIdsForNewPlayers_dto,
   "details" : details_dto,
})
'''




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



# if dict:
    # if keys already used:
        # return
    # parse dict
    # render description 


def _update_schema_list_from_dict(
    Dict: dict, 
    schema_list: list[Schema],
    schema_name: SchemaName) -> list[Schema]:

    assert(isinstance(Dict, dict))

    # may want to have a dict tracking schema entries
    if not isinstance(Dict, dict) or Dict.keys() in [
        fields.keys() for fields in [
            schema["schema_fields_dict"] for schema in schema_list
            ]
        ]:
        return schema_list

    updated_schema_list: list[Schema] = []
    schema_fields_dict: SchemaFieldsDict = OrderedDict{}


    for key, value in Dict.items():

        field_name: SchemaFieldName = str(key)
        schema_field_type: SchemaFieldType

        if isinstance(value, dict):
            schema_field_type = to_camel_case(key) + "_dto"
            updated_schema_list = _update_schema_list_from_dict(value, schema_list, schema_field_type)
            # a new schema has been added to the list. The name of this schema is the field type of Dict[key]

        elif isinstance(value, list):
            schema_field_type = to_camel_case(key) + "_dto"
            updated_schema_list = _update_schema_list_from_list(value, schema_list, schema_field_type)

        else:
            schema_field_type = type(value).__name__
            return schema_list

        schema_fields_dict[field_name] = schema_field_type

    if updated_schema_list:
        updated_schema_list.append({"schema_name" : f"{schema_name}",  "schema_fields_dict" : {schema_fields_dict}})
    

    return updated_schema_list
    

def render_object_list(primary_object: Any, object_name: ObjectTypeName) -> ObjectTypeDespcritorDict:

    schema_list : list[Schema] = []


    if isinstance(object, dict):
        schema_list = _update_schema_list_from_dict(primary_object, schema_list, object_name)

    elif isinstance(object, list):
        schema_list = _update_schema_list_from_list(primary_object, schema_list, object_name)

    return schema_list
    