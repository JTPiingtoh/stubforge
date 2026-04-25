from inspect import signature
from typing import Callable, Any, TypeAlias, Literal, TypedDict, assert_type
import inspect
import json

from collections import OrderedDict
from stubforge.dict_extras import ordered_dict_updated
from stubforge.stubforge_types import *

JSON: TypeAlias = dict | list
typed_json: TypeAlias = dict | str

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

SigStubSchemaMapping: TypeAlias = OrderedDict[Literal["stub", "schema_list"], Any]
StubSchemaMapping: TypeAlias = OrderedDict[str, SigStubSchemaMapping] 

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
        [stub_result.append(c) for c in f"def {func_name}{func_signiture} -> {func_return_type}: ...\n"] # type: ignore [func-returns-value] 

    elif isinstance(result, list):
        mutable_field_type = MutableString("")
        parse_list(result, schema_list, type_count, func_name, mutable_field_type)
        func_return_type = mutable_field_type.get_string()
        [stub_result.append(c) for c in f"def {func_name}{func_signiture} -> {func_return_type}: ...\n"] # type: ignore [func-returns-value]

    # Load previous types and stubs (if any)
    func_file_path = inspect.getfile(func)
    func_file_name = func_file_path.split("\\")[-1]
    func_base_path = func_file_path.removesuffix(func_file_name)
    stub_file_path = func_base_path + f"\\{func_file_name}i" # .pyi


    # base on the new types, write to the typing and stub files
    if not typing_file_name:
        # create a typing file in the same dir as func
        typing_file_name = "Types.py"

    rendered_stub: str = "".join(stub_result)

    # update the types and stubs, adding any new or changed types in order
    with open(f"STUBS_TYPES_{func_file_path.replace("\\", "_").removesuffix(".py")}.json".replace(":", ""), "r+") as namespace_f:

        # search for function signiture
        
        # get just the func args
        func_sig = func.__name__ + str(inspect.signature(func).replace(return_annotation=inspect.Signature.empty))

        # therefore need a function that returns whether there is a json and whether there is a key
       
        
        def read_json() -> StubSchemaMapping | None:
            try:
                return json.load(namespace_f)
            except json.decoder.JSONDecodeError:
                return None

        read_stub_schema: StubSchemaMapping | None = read_json()
        
        def read_stubs_schema_from_json() ->  SigStubSchemaMapping | None: 
            try:
                if read_stub_schema:
                    assert_type(read_stub_schema, StubSchemaMapping)
                    return read_stub_schema[func_sig]
                return None
            except KeyError:
                return None

        read_func_stub_schema: SigStubSchemaMapping | None = read_stubs_schema_from_json()

        new_stub_schema: StubSchemaMapping
        new_func_stub_schema: SigStubSchemaMapping

        def update_namespace_f(new_stub_schema: StubSchemaMapping):
            namespace_f.truncate(0)
            namespace_f.seek(0)
            json.dump(new_stub_schema, namespace_f, indent=4)

        # if json (and therefore dict) not present
        if not read_stub_schema and not read_func_stub_schema:
            
            new_func_stub_schema = OrderedDict(
                {
                    "stub" : rendered_stub,
                    "schema_list" : schema_list
                }
            )
            new_stub_schema = OrderedDict({func_sig : new_func_stub_schema})
            update_namespace_f(new_stub_schema)

        # elif json and no dict, populate
        elif read_stub_schema and not read_func_stub_schema:
                
            assert_type(read_stub_schema, StubSchemaMapping)
            new_stub_schema = read_stub_schema

            new_func_stub_schema = OrderedDict(
                {
                    "stub" : rendered_stub,
                    "schema_list" : schema_list
                }
            )
            new_stub_schema[func_sig] = new_func_stub_schema
            update_namespace_f(new_stub_schema)
                

        # elif json and key, update
        elif read_stub_schema and read_func_stub_schema:

            assert_type(read_func_stub_schema, SigStubSchemaMapping)
            assert_type(read_stub_schema, StubSchemaMapping)
                
            new_stub_schema = read_stub_schema
            new_func_stub_schema = read_func_stub_schema

            if stub_updated := ordered_dict_updated(new_func_stub_schema,"stub", rendered_stub):
                new_stub_schema[func_sig] = new_func_stub_schema

            if schema_list_updated := ordered_dict_updated(new_func_stub_schema,"schema_list", schema_list):
                new_stub_schema[func_sig] = new_func_stub_schema

            if schema_list_updated or stub_updated:
                update_namespace_f(new_stub_schema)
        




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


