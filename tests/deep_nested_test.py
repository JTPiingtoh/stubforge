from stubforge import tools
import json
import pathlib

parent = pathlib.PurePath(__file__).parent
def deep_nested_test():
    with open(f"{parent}/deep_nested_test.json", "r") as f:
        return json.load(f)


tools.stub_builder(deep_nested_test)