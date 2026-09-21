from inspect import signature
from typing import Callable, Any, TypeAlias, Literal
import inspect
import json
import pathlib
import os

from collections import OrderedDict
from stubforge.namespace import render_new_stub_schema
from stubforge.stubforge_types import *
from stubforge.parsers import to_camel_case, render_schema_list

StubSchemaMapping: TypeAlias = OrderedDict[Literal["stub", "schema_list"], Any]
SigStubSchemaMapping: TypeAlias = OrderedDict[str, StubSchemaMapping] 

# TODO: re-write this fucking mess
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
    
    func_name: str = func.__name__
    schema_name: SchemaName = to_camel_case(func_name)
    func_signiture = signature(func)
    # type_count = TypeCount()
    rendered_stub: str = ""
    

    # schema_list = parse_object(result, schema_name, func_name)
    # schema_name
    try:
        schema_list = render_schema_list(result, schema_name)
        rendered_stub = f"def {func_name}{func_signiture} -> {schema_name}: ...\n"] # type: ignore [func-returns-value]

    except RecursionError:
        raise RecursionError(f"Returned object from {func_name} is too nested.")

    # Load previous types and stubs (if any)
    func_file_path = inspect.getfile(func)
    func_file_name = func_file_path.split("\\")[-1]
    func_base_path = func_file_path.removesuffix(func_file_name)
    stub_file_path = pathlib.Path(f"{func_base_path}\\{func_file_name}i") # .pyi

    # base on the new types, write to the typing and stub files
    if not typing_file_name:
        # create a typing file in the same dir as func
        typing_file_name = "Types.py"
    typing_path = pathlib.Path(f"{func_base_path}\\{typing_file_name}")

    ingots_dir = pathlib.Path(f"{func_base_path}.stubforge_ingots")
    ingot_file_path = pathlib.Path(f"{ingots_dir}/{func_file_name.removesuffix(".py")}.json".replace("/", "\\"))

    if not ingots_dir.exists():
        os.mkdir(ingots_dir)

    for path in ingot_file_path, stub_file_path, typing_path:
        print(path)
        if not path.exists():
            with open(path, "w") as _:
                pass 


    # update the types and stubs, adding any new or changed types in order
    # BUG: files will no re-write so long as ingot file exists with no changes to schema.
    # This means if user changes stub or typing file and then runs this function, the former 2 files
    # will not update. Add last updated to ingot and compare to stub and typing files 

    with open(ingot_file_path, "r+") as ingot_f, \
        open(stub_file_path, "r+") as stub_f, \
        open(typing_path, "r+") as typing_f:

        # search for function signiture
        
        # get just the func args
        func_sig = func.__name__ + str(inspect.signature(func).replace(return_annotation=inspect.Signature.empty))
    
        new_sig_stub_schema_mapping: SigStubSchemaMapping | None = render_new_stub_schema(
            ingot_f,
            func_sig,
            rendered_stub,
            schema_list
        )

        if not new_sig_stub_schema_mapping:
            return 

        print(func_file_name)
        print("passed")

        for f in [ingot_f, stub_f, typing_f]:
            f.truncate(0)
            f.seek(0)

        json.dump(new_sig_stub_schema_mapping, ingot_f, indent=4)

        stub_py: str = f"from typing import TypedDict\nfrom {typing_file_name.removesuffix(".py")} import *\n\n"
        # write updated stub to file
        for stub in [new_sig_stub_schema_mapping[f_sig]["stub"] for f_sig in new_sig_stub_schema_mapping.keys()]:
            # write to stub_f
            stub_py += stub + "\n"

        print(stub_py)
        stub_f.write(stub_py)

        typing_py: str = "from typing import TypedDict\n\n"
        for schema_list, f_sig in [[new_sig_stub_schema_mapping[f_sig]["schema_list"], f_sig] for f_sig in new_sig_stub_schema_mapping.keys()]:
            typing_py += f"# Schema for the funciton {f_sig} #\n"
            for schema in schema_list:
                typing_py += f'{schema["schema_name"]} = TypedDict("{schema["schema_name"]}", {{'
                for field_name, field_type in schema["schema_fields"].items():
                    typing_py += f'\n   "{field_name}" : {field_type},'
                typing_py += "\n})\n\n"

        typing_f.write(typing_py)        


