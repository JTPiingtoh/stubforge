from collections import OrderedDict
from typing import TypeAlias, TypedDict

FieldName: TypeAlias = str
FieldType: TypeAlias = str
# The name of a schema
SchemaName: TypeAlias = str

class Field(TypedDict):
    field_name: FieldName
    field_type: FieldType

# The fields and types of a schema, stored in a list
SchemaFields: TypeAlias = OrderedDict[FieldName, FieldType]

# An object that contains the name of the schema, and its fields 
class Schema(TypedDict):
    schema_name: SchemaName
    schema_fields: SchemaFields

class MutableString:
    def __init__(self, s: str):
        self.data = s
    def set_string(self, s):
        self.data = s
    def get_string(self):
        return self.data