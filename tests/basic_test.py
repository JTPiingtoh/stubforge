from stubforge import tools
import json
import pathlib

parent = pathlib.PurePath(__file__).parent

@tools.maintained(typing_file_path = "path_to_file", stub_file_path = "path_to_file", return_object_name="test")
def test():
    with open(f"{parent}/basic_test.json", "r") as f:
        return json.load(f)


tools.stub_builder(test)

