from stubforge import tools
import json
import pathlib

parent = pathlib.PurePath(__file__).parent
def array_of_arrays_test():
    with open(f"{parent}/array_of_arrays_test.json", "r") as f:
        return json.load(f)


tools.stub_builder(array_of_arrays_test)