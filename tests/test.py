from stubforge import tools
import json
import pathlib

parent = pathlib.PurePath(__file__).parent
def test():
    with open(f"{parent}/test_response.json", "r") as f:
        return json.load(f)

def test2():
    with open(f"{parent}/test_response_2.json", "r") as f:
        return json.load(f)

def match_v4(foo=None):
    with open(f"{parent}/match_response.json", "r") as f:
        return json.load(f)

def list_test():
        with open(f"{parent}/list_test.json", "r") as f:
            return json.load(f)


tools.stub_builder(test)




# tools.stub_builder(test2)
# tools.stub_builder(match_v4)
# tools.stub_builder(list_test)
