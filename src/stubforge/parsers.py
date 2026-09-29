from inspect import signature
from typing import Callable, Any, TypeAlias, Literal, TypedDict, assert_type
import inspect
import json

from dataclasses import dataclass
from collections import OrderedDict
from stubforge.dict_extras import ordered_dict_updated
from stubforge.namespace import render_new_stub_schema
from stubforge.stubforge_types import *
from stubforge.helpers import retrieve_schema_name_from_schema_list, to_camel_case


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
    list_object: list, 
    schema_list: list[Schema], 
    parent_object_name: SchemaName
    ) -> tuple[list[Schema], SchemaFieldType]:

    type_names_in_list = []
    sub_dtos: int = 0
    
    for item in list_object:
        
        type_name: str | None

        if isinstance(item, dict) and (type_name := retrieve_schema_name_from_schema_list(item, schema_list)):
            pass
                
        elif isinstance(item, dict):
            type_name = parent_object_name + f"_list_dto_{sub_dtos}"
            sub_dtos+=1
            schema_list = _update_schema_list_from_dict(item, schema_list, type_name)

        elif isinstance(item, list):
            type_name = parent_object_name + f"_sublist_{sub_dtos}"
            sub_dtos+=1
            schema_list, type_name = _update_schema_list_from_list(item, schema_list, parent_object_name=type_name)
        
        else:
            type_name = type(item).__name__ 


        type_names_in_list.append(type_name)

    list_field_type: SchemaFieldType

    # BUG: Lists that do not use built in types must be treated as a new object, like a schema, to prevent masking from the schema checker
    if len(type_names_in_list) == 0:
        list_field_type = f"None"

    elif all(t == type_names_in_list[0] for t in type_names_in_list):
        list_field_type = f"list[{type_names_in_list[0]}]"

    else:
        unique_types_names = list(set(type_names_in_list))
        unique_types_names.sort()
        list_field_type = f"list[{" | ".join( unique_types_names )}]"

    return schema_list, list_field_type


def _update_schema_list_from_dict(
    dict_object: dict, 
    schema_list: list[Schema],
    object_name: SchemaName,
    settings: Settings
    ) -> list[Schema]:

    assert(isinstance(dict_object, dict))

    schema_fields_dict: SchemaFieldsDict = OrderedDict()


    for key, value in dict_object.items():

        field_name: FieldName = str(key)
        schema_field_type: SchemaFieldType | None

        # if settings.trust_JSON_consistency = DO_TRUST_JSON
        # schema_retriever
        if isinstance(value, dict) and (schema_field_type := retrieve_schema_name_from_schema_list(value, schema_list)):
            pass

        elif isinstance(value, dict):
            schema_field_type = to_camel_case(key) + "_dto"
            schema_list = _update_schema_list_from_dict(value, schema_list, schema_field_type, settings)

        elif isinstance(value, list):
            schema_list, schema_field_type = _update_schema_list_from_list(value, schema_list, parent_object_name=field_name)

        else:
            schema_field_type = type(value).__name__
            
        schema_fields_dict[field_name] = schema_field_type

    # todo: change schema
    new_schema: Schema = {"schema_name" : object_name, "schema_fields_dict" : schema_fields_dict}
    schema_list.append(new_schema)    

    return schema_list
    

def render_object_list(
        primary_object: Any, 
        object_name: SchemaName, 
        settings: Settings = Settings(
            DO_NOT_TRUST_JSON_CONSISTENCY, 
            DEFAULT_MAX_RECURSION_DEPTH, 
            DO_FORCE_REWRITE
            )
        ) -> list[Schema] | None:

    schema_list : list[Schema] = []

    if isinstance(primary_object, dict):
        schema_list = _update_schema_list_from_dict(primary_object, schema_list, object_name, settings)
        return schema_list

    elif isinstance(primary_object, list):
        schema_list, _ = _update_schema_list_from_list(primary_object, schema_list, object_name)
        return schema_list

    else: 
        return None

    