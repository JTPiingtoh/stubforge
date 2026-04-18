from stubforge import tools
import json



def test():
    with open("test_response.json", "r") as f:
        return json.load(f)
    
def match_v4(foo=None):
    with open("match_response.json", "r") as f:
        return json.load(f)
    
tools.stub_builder(test)
tools.stub_builder(match_v4)