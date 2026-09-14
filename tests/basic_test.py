from stubforge import tools
import json
import pathlib

parent = pathlib.PurePath(__file__).parent
def test():
    with open(f"{parent}/basic_test.json", "r") as f:
        return json.load(f)



tools.stub_builder(test)

