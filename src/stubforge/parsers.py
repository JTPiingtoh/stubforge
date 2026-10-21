from typing import Any
from functools import wraps

from collections import OrderedDict

from stubforge.stubforge_types import *
from stubforge.helpers import retrieve_dto_name_from_dto_index_on_keys, to_camel_case
from stubforge.config import Settings

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


# trust consistency
def try_type_retrieval(
    o: object,
    object_key: str,
    object_name: DictKeyName,
    object_index: ObjectTypeIndex
) -> tuple[ObjectTypeIndex, DictValueType | None]:

    if not isinstance(o, dict):
        return object_index, None

    assert(isinstance(o, dict))

    if retrieved_name := object_index[
            sorted(
                    list(o.keys())
                )
        ][DTONameIndex]:
        return object_index, retrieved_name

    return object_index, None

    
def try_probe_dict_in_dict(
    o: object,
    object_key: str,
    object_name: DictKeyName,
    object_index: ObjectTypeIndex
) -> tuple[ObjectTypeIndex, DictValueType | None]:

    if not isinstance(o, dict):
        return object_index, None

    assert(isinstance(o, dict))
    
    dict_value_type: DictValueType = to_camel_case(object_key) + "_dto"

    # remove settings
    return _update_object_index_from_dict(o, object_index, dict_value_type), dict_value_type


def try_probe_list_in_dict(
    o: object,
    object_key: str,
    object_name: DictKeyName,
    object_index: ObjectTypeIndex
) -> tuple[ObjectTypeIndex, DictValueType | None]:

    if not isinstance(o, list):
        return object_index, None

    assert(isinstance(o, list))

    return _update_object_index_from_list(o, object_index, object_name)


def default_object_type_from_object_in_dict(
    o: object,
    object_key: str,
    object_name: DictKeyName,
    object_index: ObjectTypeIndex
) -> tuple[ObjectTypeIndex, DictValueType | None]:

    dict_value_type: DictValueType = type(o).__name__

    assert(not (dict_value_type in ["string", "dict"]))

    return object_index, dict_value_type



def parse_homogenous_list():
    # Assumes all items in a list are of the same type. probes only 
    # the first item, if any.

    pass

def parse_heterogeneous_list():
    # Assumes list items are not all of the same type, probing each one,
    # up to a use defined limit
    pass

def parse_heterogeneous_list_and_raise_hetero():
    # Same as parse_heterogeneous_list(), but raises a warning if the
    # list is not if a singular type.
    pass


def _update_object_index_from_list(
    list_object: list, 
    schema_list: list[Schema], 
    parent_object_name: DTOName
    ) -> tuple[list[Schema], DictValueType]:

    type_names_in_list = []
    sub_dtos: int = 0
    
    for item in list_object:
        
        type_name: str | None

        if isinstance(item, dict) and (type_name := retrieve_dto_name_from_dto_index_on_keys(item, schema_list)):
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

    list_field_type: DictValueType

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


def _update_object_index_from_dict(
    dict_object: dict, 
    object_index: ObjectTypeIndex,
    object_name: DTOName,
    settings: Settings
    ) -> ObjectTypeIndex:

    assert(isinstance(dict_object, dict))

    schema_fields_dict: SchemaFieldsDict = OrderedDict()

    

    for key, value in dict_object.items():
        dto_name: DictKeyName = str(key)

        # write policies in to THIS file, include to tools. pass as list, policies will also take policy list/ composed list as arg

        dict_value_type: DictValueType | None
        # Check whether consistency is trusted. If it is, retrive the field type if already seen, else par
        if settings.trust_keyvalue_consistency and isinstance(value, dict) and (retrieved_value_type := retrieve_dto_name_from_dto_index_on_keys(value, object_index)):
            dict_value_type = retrieved_value_type

        
        elif isinstance(value, dict):
            dict_value_type = to_camel_case(key) + "_dto"
            object_index = _update_schema_list_from_dict(value, object_index, dict_value_type, settings)

        elif isinstance(value, list):
            object_index, dict_value_type = _update_schema_list_from_list(value, object_index, parent_object_name=dto_name)

        else:
            dict_value_type = type(value).__name__
        
        schema_fields_dict[dto_name] = dict_value_type


    for key, value in dict_object.items():

        dto_name: DictKeyName = str(key)
        dict_value_type: DictValueType | None

        for policy in settings.dict_probe_policies:
            object_index, dict_value_type = policy(value, dto_name)


    # todo: change schema
    new_schema: Schema = {"schema_name" : object_name, "schema_fields_dict" : schema_fields_dict}
    object_index.append(new_schema)    

    return object_index
    


def render_object_list(
    primary_object: Any, 
    object_name: DTOName, 
    probe_settings: list[DictProbePolicy]
    ) -> list[Schema] | None:

    object_index: ObjectTypeIndex = OrderedDict()
    object_list : list[Schema] = []

    if isinstance(primary_object, dict):
        object_list = _update_schema_list_from_dict(primary_object, object_list, object_name, probe_settings)
        return object_list

    elif isinstance(primary_object, list):
        object_list, _ = _update_schema_list_from_list(primary_object, object_list, object_name)
        return object_list

    else: 
        return None

    