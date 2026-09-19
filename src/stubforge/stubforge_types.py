from collections import OrderedDict
from typing import TypeAlias, TypedDict

FieldType: TypeAlias = str
# The name of a schema
ObjectName: TypeAlias = str
SchemaName: TypeAlias = str

class Field(TypedDict):
    field_name: ObjectName
    field_type: FieldType

# The fields and types of a schema, stored in a dict
SchemaFields: TypeAlias = OrderedDict[ObjectName, FieldType]

# An object that contains the name of the schema, and its fields 
class Schema(TypedDict):
    schema_name: ObjectName
    schema_fields: SchemaFields

class MutableString:
    def __init__(self, s: str):
        self.data = s
    def set_string(self, s):
        self.data = s
    def get_string(self):
        return self.data

