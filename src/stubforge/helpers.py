from stubforge.stubforge_types import *


def to_camel_case(text: str) -> str:
        s = text.replace("-", " ").replace("_", " ")
        s = s.split()
        if len(text) == 0:
            return text
        return s[0] + ''.join(i.capitalize() for i in s[1:])


def sorted_dict_keys(d: dict) -> tuple[DictKey, ...]:

    keys: list[str] = [str(key) for key in d.keys()]

    return tuple(sorted(keys))
    

def retrieve_dto_name_from_dto_index_on_keys(dict_object: dict, object_index: ObjectTypeIndex) -> DTOName | None:

    keys = sorted_dict_keys(dict_object)

    retrieved_name: DTOName | None = None

    try:
        retrieved_name = object_index[keys].dto_name
    except:
        pass

    return retrieved_name

 
def convert_index_to_list(index: ObjectTypeIndex) -> list[DTOContainer]:
    return [cont for cont in index.values()]

    
def convert_list_to_index(containers: list[DTOContainer]) -> ObjectTypeIndex:
    index: ObjectTypeIndex = OrderedDict()

    for container in containers:
        index[container.dto_field_names] = container

    return index


def render_typing_py(object_list: list[DTOContainer], func_name: str) -> str:

    typing_py = f"from typing import TypedDict\n\n# Objects for the function {func_name}\n\n"
    for o in object_list:
        typing_py += f'{o.dto_name} = TypedDict("{o.dto_name}", {{\n'

        for field_name, field_type in o.dto_fields:
            typing_py += f'"{field_name} : {field_type},\n'

            typing_py += "})\n\n"

    return typing_py