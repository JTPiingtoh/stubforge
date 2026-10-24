from collections import OrderedDict
from typing import TypeAlias, TypedDict, Any, Callable
from dataclasses import dataclass

from stubforge.config import Settings

# The name of a DTO
DTOName: TypeAlias = str
DictKey: TypeAlias = str
DictValueType: TypeAlias = str

# DictFields: TypeAlias = tuple[DictKey]

DictValueTypes: TypeAlias = tuple[DictValueType]

@dataclass
class DTOContainer:
    dto_name: DTOName
    dto_fields: DictFields
    dto_field_types: DictValueTypes

ObjectTypeIndex: TypeAlias = OrderedDict[DictFields, DTOContainer]

DictProbePolicy: TypeAlias = Callable[
    [object, DictKey, ObjectTypeIndex, Settings],
    tuple[ObjectTypeIndex, DictValueType | None],
]




_sentinel = object()



    

        

