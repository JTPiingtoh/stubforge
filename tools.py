from inspect import signature
from typing import Callable, Any, TypeAlias, Literal, TypedDict
import inspect
import json

JSON: TypeAlias = dict | list
typed_sjon: TypeAlias = dict | str

FieldName: TypeAlias = str
FieldType: TypeAlias = str
# The name of a schema
SchemaName: TypeAlias = str

class Field(TypedDict):
    field_name : FieldName
    field_type : FieldType

# The fields and types of a schema, stored in a list
SchemaFields: TypeAlias = list[Field]

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

    if not isinstance(result, dict) or result.keys() in [schema["schema_fields"] for schema in schema_list]:
        return

    # build a list containing names and types of this dict
    schema_fields: SchemaFields = []
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

        schema_fields.append({"field_name" : field_name, "field_type" : field_type})
    
    type_count.count += 1
    schema_name = f"{func_name}" + "_TYPE" + f"_{type_count.count}"
    schema_list.append({"schema_name" : f"{schema_name}", "schema_fields" : schema_fields})

    return



def stub_builder(func: Callable[[], JSON], typing_file_path: str | None, *args, **kwargs) -> None:
    '''
    Takes a function that returns a JSON object, and builds a stub to be inserted into
    a pyi file of the same name as the function's module.
    '''
    if not callable(func):
        raise ValueError(f"{func} is not a function.")
    
    result: JSON | Any = func(*args, **kwargs)

    if not type(result) == JSON:
        raise ValueError(f"{func} does not appear to return a json object")
    
    assert(type(result) == JSON)
    
    # Store the types found in the result
    
    func_name = func.__name__
    func_signiture = signature(func)
    schema_list: list[Schema] = []
    type_count = TypeCount()
    stub_result = []
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

    if not typing_file_path:
        # create a typing file in the same dir as func
        typing_file_path = func_base_path + "\\typing.py"

    rendered_stub: str = "".join(stub_result)

    # update the types and stubs, adding any new or changed types in order
    with open(stub_file_path, "r+") as stub_f:
        # effect is to namespace the function
        with open(f"STUBS_{func_file_path.replace("\\", "_")}.json", "r+") as namespace_f:

            # search for function signiture
            saved_stubs: dict
            # get just the func args
            func_sig = inspect.signature(func).replace(return_annotation=inspect.Signature.empty)

            try:
                saved_stubs = json.load(namespace_f)
                # update the saved stub if args are different
                if rendered_stub != saved_stubs[func_sig]:
                    saved_stubs[func_sig] = rendered_stub

            except FileNotFoundError:
                saved_stubs = {}
                saved_stubs[func_sig] = rendered_stub

            # TODO: Handle key error

            json.dump(saved_stubs, namespace_f)



    # base on the new types, write to the typing and stub files

    
    # Generate typing file base 

