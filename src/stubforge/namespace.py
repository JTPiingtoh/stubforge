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
    schema_list: list[Schema],
    new_stub_schema: StubSchemaMapping | None
    ):
    '''
    Renders new stub_schema mapping, return None if no update has occured
    '''
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

    new_func_stub_schema: SigStubSchemaMapping

    
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