from inspect import signature
from typing import Callable, Any, TypeAlias, Literal
import inspect
import json
import pathlib
import os

from collections import OrderedDict
from stubforge.stubforge_types import *
from stubforge.parsers import update_object_index
from stubforge.dict_probe_policies import DEFUALT_DICT_PROBE_POLICIES
from stubforge.helpers import *



# TODO: re-write this fucking mess
def stub_builder(
    func: Callable[[], dict | list | Any], 
    typing_file_name: str | None = None,
    stub_file_name: str | None = None
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
    
    func_name: str = func.__name__
    object_name: DTOName = to_camel_case(func_name) + "_dto"
    func_signiture = signature(func)

    func_file_path = inspect.getfile(func)
    func_file_name = func_file_path.split("\\")[-1]
    func_base_path = func_file_path.removesuffix(func_file_name)
    
    if not stub_file_name:
        stub_file_name = func_file_name
    stub_file_path = pathlib.Path(f"{func_base_path}\\{func_file_name}i") # .pyi

    if not typing_file_name:
        # create a typing file in the same dir as func
        typing_file_name = "Types.py"
    typing_file_path = pathlib.Path(f"{func_base_path}\\{typing_file_name}")

    # Ingots are JSON files created for each python typing file created using stubforge. They contain an index of function names, with theirs stubs and dict_lists
    ingots_dir = pathlib.Path(f"{func_base_path}.stubforge_ingots")
    ingot_file_path = pathlib.Path(f"{ingots_dir}/{typing_file_name.replace(".py", ".json").replace("/", "\\")}")

    if not ingots_dir.exists():
        os.mkdir(ingots_dir)

    for path in ingot_file_path, stub_file_path, typing_file_path:
        print(path)
        if not path.exists():
            with open(path, "w") as _:
                pass 

    object_index: ObjectTypeIndex | None = None
    
    # convert the ingot index
    with open(ingot_file_path, "r+") as ingot_f, \
        open(typing_file_path, "r+") as typing_f, \
        open(stub_file_path, "r+") as stub_f:

        try:
            object_list = json.load(ingot_f)
            object_index = convert_list_to_index(object_list)

        except json.JSONDecodeError:
            object_index = OrderedDict()

        for f in ingot_f, typing_f, stub_f:
            f.truncate()
            f.seek(0)

        rendered_stub: str = f"from typing import TypedDict\nfrom {typing_file_name.removesuffix(".py")} import {object_name}\n\n"

        # TODO: move this to the user
        settings = Settings(
            trust_keyvalue_consistency=True,
            max_recursion_depth=30,
            force_rewrite=True,
            trust_list_homogeneity=True,
            dict_probe_policies=DEFUALT_DICT_PROBE_POLICIES
        )
        
        try:
            object_index = update_object_index(result, object_name, object_index, settings)

            if object_index:
                rendered_stub += f"def {func_name}{func_signiture} -> {object_name}: ...\n" # type: ignore [func-returns-value]

            else:
                rendered_stub += f"def {func_name}{func_signiture} -> {type(result).__name__}: ...\n" # type: ignore [func-returns-value]

            stub_f.write(rendered_stub)

        except RecursionError:
            raise RecursionError(f"Returned object from {func_name} is too nested.")

        object_list = convert_index_to_list(object_index)
        typing_py: str = render_typing_py(object_list, func_name)


    # update typing and ingot
    

        print(typing_py)
    

    
    

