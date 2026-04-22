from inspect import signature
from typing import Callable, Any, TypeAlias, Literal, TypedDict
import inspect
import json

from collections import OrderedDict
from stubforge.dict_extras import ordered_dict_updated

JSON: TypeAlias = dict | list
typed_json: TypeAlias = dict | str

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


class TypeCount:
    count = 0


def parse_list(value: list, schema_list: list[Schema], type_count: TypeCount, func_name: str, mutable_field_type: MutableString):

    type_names_in_list = []
    for obj in value:
        type_name: str
        if isinstance(obj, dict):
            parse_dict(obj, schema_list, type_count, func_name)
            type_name = schema_list[-1]["schema_name"]
        else:
            type_name = type(obj).__name__   
        type_names_in_list.append(type_name)

    if len(type_names_in_list) == 0:
        mutable_field_type.set_string(f"list[{type_names_in_list[0]}]")
    elif all(t == type_names_in_list[0] for t in type_names_in_list):
        mutable_field_type.set_string(f"list[{type_names_in_list[0]}]")
    else:
        mutable_field_type.set_string(f"list[{" | ".join( list(set(type_names_in_list)) )}]")


def parse_dict(result: dict, schema_list: list[Schema], type_count: TypeCount, func_name: str):


    if not isinstance(result, dict) or result.keys() in [fields.keys() for fields in [schema["schema_fields"] for schema in schema_list]]:
        return

    # build a list containing names and types of this dict
    schema_fields: SchemaFields = OrderedDict()
    for key, value in result.items():

        field_name: FieldName = str(key)
        field_type: FieldType

        if isinstance(value, dict):
            parse_dict(value, schema_list, type_count, func_name)
            field_type = schema_list[-1]["schema_name"]

        elif isinstance(value, list):
            mutable_field_type = MutableString("")
            parse_list(value, schema_list, type_count, func_name, mutable_field_type)
            field_type = mutable_field_type.get_string()

        else:
            field_type = type(value).__name__

        schema_fields[field_name] = field_type
    
    type_count.count += 1
    schema_name = f"{func_name}" + "_TYPE" + f"_{type_count.count}"
    schema_list.append({"schema_name" : f"{schema_name}", "schema_fields" : schema_fields})

    return



def stub_builder(func: Callable[[], JSON], typing_file_name: str | None = None, *args, **kwargs) -> None:
    '''
    Takes a function that returns a JSON object, and builds a stub to be inserted into
    a pyi file of the same name as the function's module.
    '''
    if not callable(func):
        raise ValueError(f"{func} is not a function.")
    
    result: JSON | Any = func(*args, **kwargs)

    if not isinstance(result, (dict, list)):
        raise ValueError(f"{func} does not appear to return a json object")
    
    
    # Store the types found in the result
    
    func_name = func.__name__
    func_signiture = signature(func)
    schema_list: list[Schema] = []
    type_count = TypeCount()
    stub_result: list[str] = []
    func_return_type: SchemaName

    if isinstance(result, dict):
        parse_dict(result, schema_list, type_count, func_name)
        # final entry to the schema list will be the schema of the json file itself
        func_return_type = schema_list[-1]["schema_name"]
        [stub_result.append(c) for c in f"def {func_name}{func_signiture} -> {func_return_type}: ...\n"]

    elif isinstance(result, list):
        mutable_field_type = MutableString("")
        parse_list(result, schema_list, type_count, func_name, mutable_field_type)
        func_return_type = mutable_field_type.get_string()
        [stub_result.append(c) for c in f"def {func_name}{func_signiture} -> {func_return_type}: ...\n"]

    # Load previous types and stubs (if any)
    func_file_path = inspect.getfile(func)
    func_file_name = func_file_path.split("\\")[-1]
    func_base_path = func_file_path.removesuffix(func_file_name)
    stub_file_path = func_base_path + f"\\{func_file_name}i" # .pyi

    _STUB: str = "STUB"
    _SCHEMA_LIST: str = "SCHEMA_LIST"

    # base on the new types, write to the typing and stub files
    if not typing_file_name:
        # create a typing file in the same dir as func
        typing_file_name = "Types.py"

    rendered_stub: str = "".join(stub_result)

    # update the types and stubs, adding any new or changed types in order
    with open(f"STUBS_TYPES_{func_file_path.replace("\\", "_").removesuffix(".py")}.json".replace(":", ""), "r+") as namespace_f:

            # search for function signiture
            saved_stubs_schema : dict | object
            saved_stub: OrderedDict
            stub_updated: bool
            schema_list_updated: bool
            func_saved_stubs_schema: dict[Literal["stub", "schema_list"], Any] | object
            # get just the func args
            func_sig = func.__name__ + str(inspect.signature(func).replace(return_annotation=inspect.Signature.empty))
    
            _json_sentinal = object()
            _dict_sentinal = object()

            # therefore need a function that returns whether there is a json and whether there is a key
            def load_json() -> dict | object:
                try:
                    return json.load(namespace_f)
                except json.decoder.JSONDecodeError:
                    return _json_sentinal

            saved_stubs_schema = load_json()

            def load_stubs_schema_from_json() -> dict[Literal["stub", "schema_list"], Any] | object:
                if saved_stubs_schema != _json_sentinal:
                    assert isinstance(saved_stubs_schema, dict)
                    try:
                        return saved_stubs_schema[func_sig]
                    except KeyError:
                        return _dict_sentinal
                    
                return _dict_sentinal
            
            func_saved_stubs_schema = load_stubs_schema_from_json()
            # TODO: remove double call to load_json

            match (saved_stubs_schema, func_saved_stubs_schema):
            # if no json, create json and populate
                case (_json_sentinal, _dict_sentinal):
                    func_saved_stubs_schema = OrderedDict(
                        {
                            func_sig : {
                                _STUB : rendered_stub,
                                _SCHEMA_LIST : schema_list
                            }
                        }
                    )
                    stub_updated, schema_list_updated = True , True
            # elif json and no key, populate
                case (dict(), _dict_sentinal):
                    func_saved_stubs_schema[func_sig] = {
                        _STUB : rendered_stub,
                        _SCHEMA_LIST : schema_list
                    }

                    stub_updated, schema_list_updated = True , True


            # elif json and key, update
                case (dict(), dict()):
                    if stub_updated := ordered_dict_updated(func_saved_stubs_schema, "stub", rendered_stub):
                        saved_stubs_schema[func_sig]["stub"] = saved_stub

                    saved_schema_list: list[Schema] = func_saved_stubs_schema["schema_list"]

                    new_fields = [fields.keys() for fields in [schema["schema_fields"] for schema in schema_list]]
                    old_fields = [fields.keys() for fields in [schema["schema_fields"] for schema in saved_schema_list]]

                    if schema_list_updated := new_fields != old_fields:
                        saved_stubs_schema[func_sig]["schema_list"] = schema_list


            if stub_updated or schema_list_updated:
                namespace_f.truncate(0)
                namespace_f.seek(0)
                json.dump(saved_stubs_schema, namespace_f)


    # with open(stub_file_path, "r+") as stub_f:
    #     # effect is to namespace the function
        

    #     stub_py: str = f"from typing import TypedDict\nfrom {typing_file_name.removesuffix(".py")} import *\n\n"
    #     print(stubs_updated)
    #     if stubs_updated:
    #         # write updated stub to file
    #         for stub in saved_stubs.values():
    #             # write to stub_f
    #             stub_py += stub + "\n"
            
    #         stub_f.write(stub_py)

    
    # typing_py: str = "from typing import TypedDict\n\n"
    # with open(func_base_path + f"\\{typing_file_name}", "r+") as f:
    #     for schema in schema_list:
    #         typing_py += f'{schema["schema_name"]} = TypedDict("{schema["schema_name"]}", {{'
    #         for field_name, field_type in schema["schema_fields"].items():
    #             typing_py += f'\n   "{field_name}" : {field_type},'
    #         typing_py += "\n})\n"

    
    #     f.write(typing_py)        


