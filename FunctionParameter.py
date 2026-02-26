from ValueType import ValueType

class FunctionParameter:

    def __init__(self, param_type: ValueType, name: str):
        self.type = param_type
        self.name = name
