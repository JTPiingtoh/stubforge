from collections import OrderedDict
from typing import TypeAlias, TypedDict, Any, Callable
from dataclasses import dataclass

from stubforge.config import Settings

# The name of a DTO
DTOName: TypeAlias = str
DictKey: TypeAlias = str
DictValueType: TypeAlias = str

DictFields: TypeAlias = tuple[DictKey, ...]

DictValueTypes: TypeAlias = tuple[DictValueType]

@dataclass
class DTOContainer:
    dto_name: DTOName
    dto_field_names: DictFields
    dto_field_types: DictValueTypes

    @property
    def dto_fields(self):
        return list(zip(self.dto_field_names, self.dto_field_types))

ObjectTypeIndex: TypeAlias = OrderedDict[DictFields, DTOContainer]

DictProbePolicy: TypeAlias = Callable[
    [object, DictKey, ObjectTypeIndex, Settings],
    tuple[ObjectTypeIndex, DictValueType | None],
]




_sentinel = object()



    

        

