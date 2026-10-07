from functools import wraps


class SchemaField:

    def __init__(self, name) -> None:
        self.name: str = name
        self._type: str | object = None

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        if not self.type == None:
            raise ValueError("Type has already been set for this field") 

        self._type = value

    @property
    def finalised(self) -> bool:
        return not self.type == None

def policy(
    f,
    d: dict,
    dict_field: SchemaField,
    schema_list: list
    ):
    @wraps(f)
    def wrap(
    d: dict,
    dict_field: SchemaField,
    schema_list: list
    ):
        if dict_field.finalised:
            return dict_field, schema_list
        