from inspect import signature
from typing import Callable, Any, TypeAlias, Literal
import inspect
import json
import pathlib
import os

from collections import OrderedDict
from stubforge.namespace import render_new_stub_schema
from stubforge.stubforge_types import *
from stubforge.parsers import to_camel_case, parse_dict, parse_list



SigStubSchemaMapping: TypeAlias = OrderedDict[Literal["stub", "schema_list"], Any]
StubSchemaMapping: TypeAlias = OrderedDict[str, SigStubSchemaMapping] 

def stub_builder(
    func: Callable[[], dict | list], 
    typing_file_name: str | None = None
    ) -> None:
    '''
    Takes a function that returns a dict or list object, and builds a stub to be inserted into
    a pyi file of the same name as the function's module.
    '''
    if not callable(func):
        raise ValueError(f"{func} is not a function.")
    
    result: dict | list | Any = func()

    if not isinstance(result, (dict, list)):
        raise ValueError(f"{func} does not appear to return a json object")
    
    
    # Store the types found in the result
    
    func_name = func.__name__
    
    schema_name = to_camel_case(func_name)
    func_signiture = signature(func)
    schema_list: list[Schema] = []
    # type_count = TypeCount()
    stub_result: list[str] = []
    func_return_type: SchemaName

    try:

        if isinstance(result, dict):
            parse_dict(result, schema_list, schema_name, func_name)
            # final entry to the schema list will be the schema of the json file itself
            func_return_type = schema_list[-1]["schema_name"]       
            [stub_result.append(c) for c in f"def {func_name}{func_signiture} -> {func_return_type}: ...\n"] # type: ignore [func-returns-value] 

        elif isinstance(result, list):
            mutable_field_type = MutableString("")
            parse_list(result, schema_list, schema_name, func_name, mutable_field_type)
            func_return_type = mutable_field_type.get_string()
            [stub_result.append(c) for c in f"def {func_name}{func_signiture} -> {func_return_type}: ...\n"] # type: ignore [func-returns-value]

    except RecursionError:
        raise RecursionError(f"Returned object from {func_name} is too nested.")

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

    ingots_dir = pathlib.Path(f"{func_base_path}.stubforge_ingots")
    ingot = pathlib.Path(f"{ingots_dir}/{func_file_name.removesuffix(".py")}.json".replace("/", "\\"))

    if not ingots_dir.exists():
        os.mkdir(ingots_dir)

    if not ingot.exists():
        with open(ingot, "w") as _:
            pass 


    # update the types and stubs, adding any new or changed types in order
    # BUG: first open breaks if ingot does not already exist

    with open(f"{ingots_dir}/{func_file_name.removesuffix(".py")}.json".replace("/", "\\"), "r+") as namespace_f, \
        open(stub_file_path, "r+") as stub_f, \
        open(func_base_path + f"{typing_file_name}", "r+") as typing_f:

        # search for function signiture
        
        # get just the func args
        func_sig = func.__name__ + str(inspect.signature(func).replace(return_annotation=inspect.Signature.empty))
    
        new_stub_schema: StubSchemaMapping | None = render_new_stub_schema(
            namespace_f,
            func_sig,
            rendered_stub,
            schema_list
        )

        if not new_stub_schema:
            return 

        print(func_file_name)
        print("passed")

        for f in [namespace_f, stub_f, typing_f]:
            f.truncate(0)
            f.seek(0)

        json.dump(new_stub_schema, namespace_f, indent=4)

        stub_py: str = f"from typing import TypedDict\nfrom {typing_file_name.removesuffix(".py")} import *\n\n"
        # write updated stub to file
        for stub in [new_stub_schema[f_sig]["stub"] for f_sig in new_stub_schema.keys()]:
            # write to stub_f
            stub_py += stub + "\n"

        stub_f.write(stub_py)

        typing_py: str = "from typing import TypedDict\n\n"
        for schema_list in [new_stub_schema[f_sig]["schema_list"] for f_sig in new_stub_schema.keys()]:
            for schema in schema_list:
                typing_py += f'{schema["schema_name"]} = TypedDict("{schema["schema_name"]}", {{'
                for field_name, field_type in schema["schema_fields"].items():
                    typing_py += f'\n   "{field_name}" : {field_type},'
                typing_py += "\n})\n\n"

        typing_f.write(typing_py)        


