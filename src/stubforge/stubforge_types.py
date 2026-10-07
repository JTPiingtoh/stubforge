from collections import OrderedDict
from typing import TypeAlias, TypedDict, Any, Callable
from dataclasses import dataclass
from enum import Enum

# The name of a schema
SchemaName: TypeAlias = str

SchemaFieldName: TypeAlias = str
SchemaFieldType: TypeAlias = str

# The fields and types of a schema, stored in a dict
# TODO:
# This can be replaced with SchemaField dataclass once policy pattern has been implemented
SchemaFieldsDict: TypeAlias = OrderedDict[SchemaFieldName, SchemaFieldType]

# An object that contains the name of the schema, and its fields 

class SchemaField:


    def __init__(self, name) -> None:
        self.name: SchemaFieldType = name
        self._type: SchemaFieldType | object = None

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

@dataclass
class Settings:
    '''
    Object containing user settings for stubforge
    '''
    trust_keyvalue_consistency: bool = DO_NOT_TRUST_JSON_KEY_VALUE_CONSISTENCY
    max_recursion_depth: int = DEFAULT_MAX_RECURSION_DEPTH 
    force_rewrite: bool = DO_FORCE_REWRITE
    trust_list_homogeneity: bool = DO_TRUST_LIST_HOMOGENEITY

    _raise_keyvalue_inconsistency = False

    @property
    def raise_keyvalue_inconsistency(self):
        return self._raise_keyvalue_inconsistency

    @raise_keyvalue_inconsistency.setter
    def raise_keyvalue_inconsistency(self, value):
        if self.trust_keyvalue_consistency == DO_TRUST_KEYVALUE_CONSISTENCY:
            raise AttributeError("Cannot raise inconsistency warning if consitency is trusted")
        self._raise_keyvalue_inconsistency: bool = value

    

        

