from ExpressionInterpreter import ExpressionInterpreter
from FunctionParameter import FunctionParameter
from ValueType import ValueType

class FunctionDefinition:

    def __init__(self, return_type: ValueType, params: [FunctionParameter], body: str):
        self.params = params
        self.body = body
        self.return_type = return_type


    def resolve(self, interpreter: ExpressionInterpreter, params: str):
        params_evaluated = [interpreter.evaluate(p.strip()) for p in params.split(',')]

        list(map(self._applyReplace, self.params, params_evaluated))
        result = interpreter.evaluate(self.body)
        return result

       
    def _applyReplace(self, param_definition, param_evaluated):

        if isinstance(param_evaluated, str):
            replacement = param_evaluated.replace('"', '""')
            replacement = f'"{replacement}"'
        else:
            replacement = str(param_evaluated)           

        self.body = self.body.replace(param_definition, replacement)
