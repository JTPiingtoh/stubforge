from typing import Callable, Any, TypeAlias, Literal, TypedDict, assert_type, TextIO
import json
from collections import OrderedDict

from stubforge.dict_extras import ordered_dict_updated
from stubforge.stubforge_types import *

SigStubSchemaMapping: TypeAlias = OrderedDict[Literal["stub", "schema_list"], Any]
StubSchemaMapping: TypeAlias = OrderedDict[str, SigStubSchemaMapping] 

def render_new_stub_schema(
    namespace_f: TextIO, 
    func_sig: str,
    rendered_stub: str, 
    schema_list: list[Schema]
    ) -> StubSchemaMapping | None:
    """
    Create or update a stub-schema mapping for a given function signature.

    This function reads an existing JSON mapping from the provided file-like
    object and conditionally inserts or updates the entry corresponding to
    `func_sig`. The mapping structure is:

        OrderedDict[str, OrderedDict[Literal["stub", "schema_list"], Any]]

    Update behavior:
    - If the JSON is empty or invalid, a new mapping is initialized.
    - If the function signature is not present, a new entry is added.
    - If the function signature exists, its "stub" and/or "schema_list"
      fields are updated only if their values differ.
    - If no changes are detected, the function returns None.

    Args:
        namespace_f (TextIO):
            File-like object containing the JSON-encoded stub-schema mapping.
            Must be readable and positioned appropriately for json.load().

        func_sig (str):
            Unique function signature used as the key in the mapping.

        rendered_stub (str):
            The rendered stub string to associate with the function signature.

        schema_list (list[Schema]):
            A list of Schema objects representing the function’s schema metadata.

    Returns:
        StubSchemaMapping | None:
            - Updated mapping if a change was made.
            - None if no update was necessary.

    Raises:
        AssertionError:
            If loaded JSON does not conform to expected type structure.

    Notes:
        - Ordering is preserved using OrderedDict.
        - Field updates rely on `ordered_dict_updated` to detect changes.
        - Invalid or empty JSON input is treated as absence of prior state.

    This docstring was generate by an LLM. The function body was written entirely by a human (JTPiingtoh).
    """
    
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

    new_stub_schema: StubSchemaMapping | None = None
    new_func_stub_schema: SigStubSchemaMapping | None = None
    
    # if json (and therefore dict) not present
    if not read_stub_schema and not read_func_stub_schema:
        
        new_func_stub_schema = OrderedDict(
            {
                "stub" : rendered_stub,
                "schema_list" : schema_list
            }
        )
        new_stub_schema = OrderedDict({func_sig : new_func_stub_schema})

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

        if not (schema_list_updated or stub_updated):
            return None

    return new_stub_schema