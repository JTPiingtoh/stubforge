# trust consistency
from stubforge.stubforge_types import *
from stubforge.parsers import _update_object_index_from_dict, _update_object_index_from_list
from stubforge.helpers import retrieve_dto_name_from_dto_index_on_keys, to_camel_case


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




DEFUALT_DICT_PROBE_POLICIES = [
    try_type_retrieval,
    try_probe_dict_in_dict,
    try_probe_list_in_dict
]