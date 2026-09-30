from typing import Any

from stubforge.stubforge_types import *
from stubforge.helpers import retrieve_schema_name_from_schema_list

def dict_value_policy(
    key_value: tuple[Any, Any], 
    schema_field: SchemaField, 
    schema_list: list[Schema]
    ) -> tuple[SchemaField, list[Schema]]:

    # TODO: add settings to schema_list, into a high level stub_forge object.
    # The stub_force objet shall be the central object containing settings and a list of schema
    # it has obtained from the parsers. The parsers shall use policies given to it by the 
    # stub_forge. The stubfore setting will contain defualts, such as 
    # else:
    #   schema_field_type = type(value).__name__
    # as well as policies given via the user. This means the TRUST JSON logic for example
    # wil be captured using different policies that use the isinstance(value, dict), as well as additioal
    # checks based upon the logic they represent


    key, value = key_value

    if isinstance(key, dict):
