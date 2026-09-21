from collections import OrderedDict
from typing import TypeAlias, TypedDict


# The name of a schema
SchemaName: TypeAlias = str

SchemaFieldName: TypeAlias = str
SchemaFieldType: TypeAlias = str

# The fields and types of a schema, stored in a dict
SchemaFieldsDict: TypeAlias = OrderedDict[SchemaName, SchemaFieldType]

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

