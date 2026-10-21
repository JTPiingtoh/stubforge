from collections import OrderedDict
from typing import TypeAlias, TypedDict, Any, Callable
from dataclasses import dataclass
from enum import Enum

# The name of a DTO
DTOName: TypeAlias = str

DictKeyName: TypeAlias = str
DictValueType: TypeAlias = str

# The fields and types of a schema, stored in a dict
# TODO:
# This can be replaced with SchemaField dataclass once policy pattern has been implemented
SchemaFieldsDict: TypeAlias = OrderedDict[DictKeyName, DictValueType]

DictFields: TypeAlias = list[DictKeyName]
DictValueTypes: TypeAlias = list[DictValueType]


DTONameIndex = 0
DictValueTypesIndex = 1

ObjectTypeIndex: TypeAlias = OrderedDict[DictFields, tuple[DTOName, DictValueTypes]]

# An object that contains the name of the schema, and its fields 

class SchemaField:


    def __init__(self, name) -> None:
        self.name: DictValueType = name
        self._type: DictValueType | object = None

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if not self.type == None:
            raise ValueError("Type has already been set for this field") 

        self._type = value

    @property
    def finalised(self) -> bool:
        return not self.type == None


class Schema(TypedDict):
    schema_name: SchemaName
    schema_fields_dict: SchemaFieldsDict


DictProbePolicy: TypeAlias = Callable[
    [object, str, DictKeyName, ObjectTypeIndex],
    tuple[ObjectTypeIndex, DictValueType | None],
]



DO_TRUST_KEYVALUE_CONSISTENCY = True
'''
    Tell stubforge to assume the value type of any any field value pair will always be consistent. 
'''
DO_NOT_TRUST_JSON_KEY_VALUE_CONSISTENCY = not DO_TRUST_KEYVALUE_CONSISTENCY
'''
    Tell stubforge to not assume the value type of any any field value pair will always be consistent. 
'''
DEFAULT_MAX_RECURSION_DEPTH = 30
DO_FORCE_REWRITE = True
'''
    Force stubforge to always rewrite the Typing.py (or user named typing files) and *.pyi files.
'''
DO_NOT_FORCE_REWRITE = not DO_FORCE_REWRITE

DO_RAISE_KEYVALUE_INCONSISTENCY_WARNING: bool = True
DO_NOT_RAISE_KEYVALUE_INCONSISTENCY_WARNING: bool = not DO_RAISE_KEYVALUE_INCONSISTENCY_WARNING 

DO_TRUST_LIST_HOMOGENEITY: bool = True
DO_NOT_TRUST_LIST_HOMOGENEITY: bool = not DO_TRUST_LIST_HOMOGENEITY



    

        

