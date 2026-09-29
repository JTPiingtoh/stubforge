from collections import OrderedDict
from typing import TypeAlias, TypedDict
from dataclasses import dataclass
from enum import Enum

# The name of a schema
SchemaName: TypeAlias = str

FieldName: TypeAlias = str
SchemaFieldType: TypeAlias = str

# The fields and types of a schema, stored in a dict
SchemaFieldsDict: TypeAlias = OrderedDict[FieldName, SchemaFieldType]

# An object that contains the name of the schema, and its fields 
class Schema(TypedDict):
    schema_name: SchemaName
    schema_fields_dict: SchemaFieldsDict

class MutableString:
    def __init__(self, s: str):
        self.data = s
    def set_string(self, s):
        self.data = s
    def get_string(self):
        return self.data


DO_TRUST_JSON_CONSISTENCY = True
'''
    Tell stubforge to assume the value type of any any field value pair will always be consistent. 
'''
DO_NOT_TRUST_JSON_CONSISTENCY = not DO_TRUST_JSON_CONSISTENCY
'''
    Tell stubforge to not assume the value type of any any field value pair will always be consistent. 
'''
DEFAULT_MAX_RECURSION_DEPTH = 30
DO_FORCE_REWRITE = True
'''
    Force stubforge to always rewrite the Typing.py (or user named typing files) and *.pyi files.
'''
DO_NOT_FORCE_REWRITE = not DO_FORCE_REWRITE

DO_RAISE_JSON_INCONSISTENCY_WARNING: bool = True
DO_NOT_RAISE_JSON_INCONSISTENCY_WARNING: bool = not DO_RAISE_JSON_INCONSISTENCY_WARNING 

@dataclass

@dataclass
class Settings:
    '''
    Object containing user settings for stubforge
    '''
    trust_JSON_consistency: bool = DO_NOT_TRUST_JSON_CONSISTENCY
    _raise_JSON_inconsistency = False
    max_recursion_depth: int = DEFAULT_MAX_RECURSION_DEPTH 
    force_rewrite: bool = DO_FORCE_REWRITE

    @property
    def raise_JSON_inconsistency(self):
        return self._raise_JSON_inconsistency

    @raise_JSON_inconsistency.setter
    def raise_JSON_inconsistency(self, value):
        if self.trust_JSON_consistency == DO_TRUST_JSON_CONSISTENCY:
            raise AttributeError("Cannot raise inconsistency warning if consitency is trusted")
        self._raise_JSON_inconsistency: bool = value

    


