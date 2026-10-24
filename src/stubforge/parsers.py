from typing import Any, cast
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
    object_name: DictKey,
    object_index: ObjectTypeIndex,
    settings: Settings
) -> tuple[ObjectTypeIndex, DictValueType | None]:

    if not isinstance(o, dict):
        return object_index, None

    assert(isinstance(o, dict))

    if retrieved_name := retrieve_dto_name_from_dto_index_on_keys(o, object_index):
        return object_index, retrieved_name

    return object_index, None

    
def try_probe_dict_in_dict(
    o: object,
    object_name: DictKey,
    object_index: ObjectTypeIndex,
    settings: Settings
) -> tuple[ObjectTypeIndex, DictValueType | None]:

    if not isinstance(o, dict):
        return object_index, None

    assert(isinstance(o, dict))
    
    dict_value_type: DictValueType = to_camel_case(object_name) + "_dto"

    # remove settings
    return _update_object_index_from_dict(o, object_index, dict_value_type, settings), dict_value_type


def try_probe_list_in_dict(
    o: object,
    object_name: DictKey,
    object_index: ObjectTypeIndex,
    settings: Settings
) -> tuple[ObjectTypeIndex, DictValueType | None]:

    if not isinstance(o, list):
        return object_index, None

    assert(isinstance(o, list))

    return _update_object_index_from_list(o, object_index, object_name, settings)


def default_object_type_from_object_in_dict(
    o: object,
    object_name: DictKey,
    object_index: ObjectTypeIndex,
    settings: Settings
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

# This function parses lists. Implementing user control for this function is tricky, as the user
# controls both how the list itself is probed, as well as the elements within it.

# The user can control whether all items or only the first is probed. As this is a binary, this behavior shall be implemented using a boolean flag

# Policies
def _update_object_index_from_list(
    list_object: list, 
    object_index: ObjectTypeIndex, 
    parent_object_name: DTOName,
    settings: Settings
    ) -> tuple[list[Schema], DictValueType]:

    type_names_in_list = []
    sub_dtos: int = 0
    sub_lists: int = 0
    
    for item in list_object:
        
        type_name: str | None

        if isinstance(item, dict) and (type_name := retrieve_dto_name_from_dto_index_on_keys(item, object_index)):
            pass
                
        elif isinstance(item, dict):
            type_name = parent_object_name + f"_list_dto_{sub_dtos}"
            sub_dtos+=1
            schema_list = _update_schema_list_from_dict(item, schema_list, type_name)

        elif isinstance(item, list):
            type_name = parent_object_name + f"_sublist_{sub_lists}"
            sub_dtos+=1
            schema_list, type_name = _update_schema_list_from_list(item, schema_list, parent_object_name=type_name)
        
        else:
            type_name = type(item).__name__ 


        type_names_in_list.append(type_name)

    list_field_type: DictValueType

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

    dict_value_types = []

    for key, value in dict_object.items():

        dict_value_type: DictValueType | None = None

        for probe_policy in settings.dict_probe_policies:
            object_index, dict_value_type = probe_policy(value, key, object_index, settings)

            if dict_value_type != None:
                break

        if not dict_value_type:
            raise ValueError(f"Probe failed to determine value type of {key} : {value}")

        # add to index
        dict_value_types.append(dict_value_type)

    dict_fields: DictFields = tuple(dict_object.keys())
    dict_value_types = tuple(dict_value_types)

    dto_container = DTOContainer(
        dto_name=object_name,
        dto_fields=dict_fields,
        dto_field_types=dict_value_types
    )

    object_index[ dict_fields ] = dto_container

    return object_index
    


def render_object_list(
    primary_object: Any, 
    object_name: DTOName, 
    settings: Settings
    ) -> ObjectTypeIndex | None:

    object_index: ObjectTypeIndex = OrderedDict()
    
    if isinstance(primary_object, dict):
        object_index = _update_object_index_from_dict(primary_object, object_index, object_name, settings)
        return object_index

    elif isinstance(primary_object, list):
        object_index, _ = _update_schema_list_from_list(primary_object, object_index, object_name, settings)
        return object_index

    return None

    