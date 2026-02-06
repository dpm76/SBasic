import re
from math import sqrt, cos, sin, tan, acos, asin, atan, log, exp, floor, pi
from random import random

class _Operator:
    def __init__(self, key, precedence, nparams, func):
        self.key = key
        self.precedence = precedence
        self.nparams = nparams
        self.func  = func


class ExpressionInterpreter:
    """Intérprete de expresiones con precedencia matemática, paréntesis y variables"""
    
    def __init__(self, numeric_vars=None, string_vars=None):
        """
        Inicializa el intérprete con diccionarios de variables.
        
        Args:
            numeric_vars: Diccionario con variables numéricas {nombre: valor}
            string_vars: Diccionario con variables de texto {nombre$: valor}
        """
        self._numeric_vars = numeric_vars if numeric_vars is not None else {}
        self._string_vars = string_vars if string_vars is not None else {}
        
        self._register_operators((
            _Operator('NEG', 5, 1, lambda a: -a),
            _Operator('SQR', 5, 1, lambda a: sqrt(a)),
            _Operator('COS', 5, 1, lambda a: cos(a)),
            _Operator('SIN', 5, 1, lambda a: sin(a)),
            _Operator('TAN', 5, 1, lambda a: tan(a)),
            _Operator('ACS', 5, 1, lambda a: acos(a)),
            _Operator('ASN', 5, 1, lambda a: asin(a)),
            _Operator('ATN', 5, 1, lambda a: atan(a)),
            _Operator('LN', 5, 1, lambda a: log(a)),
            _Operator('EXP', 5, 1, lambda a: exp(a)),
            _Operator('INT', 5, 1, lambda a: floor(a)),
            _Operator('ABS', 5, 1, lambda a: abs(a)),
            _Operator('STR$', 5, 1, lambda a: str(f"{a:g}") if isinstance(a, (int, float)) else (_ for _ in ()).throw(ValueError(f"'{a}' is not a number"))),
            _Operator('LEN', 5, 1, lambda a: len(a) if isinstance(a, str) else (_ for _ in ()).throw(ValueError(f"{a} is not a string"))),
            _Operator('SGN', 5, 1, lambda a: -1 if a < 0 else 1 if a > 0 else 0),
            _Operator('RND', 5, 0, lambda: random()),
            _Operator('PI', 5, 0, lambda: pi),
            _Operator('^', 4, 2, lambda a, b: a ** b),
            _Operator('*', 4, 2, lambda a, b: a * b),
            _Operator('/', 4, 2, lambda a, b: a / b if b != 0 else (_ for _ in ()).throw(ValueError("Zero division"))),
            _Operator('+', 3, 2, lambda a, b: a + b),
            _Operator('-', 3, 2, lambda a, b: a - b),
            _Operator('>', 2, 2, lambda a, b: a > b),
            _Operator('<', 2, 2, lambda a, b: a < b),
            _Operator('=', 2, 2, lambda a, b: a == b),
            _Operator('<=', 2, 2, lambda a, b: a <= b),
            _Operator('=<', 2, 2, lambda a, b: a <= b),
            _Operator('>=', 2, 2, lambda a, b: a >= b),
            _Operator('=>', 2, 2, lambda a, b: a >= b),
            _Operator('<>', 2, 2, lambda a, b: a != b),
            _Operator('NOT', 1, 1, lambda a: not a),
            _Operator('AND', 0, 2, lambda a, b: a and b),
            _Operator('OR', 0, 2, lambda a, b: a or b),
            _Operator('NOR', 0, 2, lambda a, b: not (a or b))
        ))

    def _register_operators(self, operators):

        self._operators = {}
        for operator in operators:
            self._operators[operator.key] = operator
    
    def _tokenize(self, expr):
        """Convierte la expresión en tokens"""
        expr = expr.strip()
        self._tokens = []
        self._expr_index = 0
        
        while self._expr_index < len(expr):
            # Saltar espacios
            if expr[self._expr_index].isspace():
                self._expr_index += 1
                continue
            
            # String entre comillas
            if expr[self._expr_index] == '"':
                j = self._expr_index + 1
                while j < len(expr) and expr[j] != '"':
                    j += 1
                if j >= len(expr):
                    raise ValueError("String sin cerrar")
                self._tokens.append(('STRING', expr[self._expr_index+1:j]))
                self._expr_index = j + 1
            
            # Operador
            elif self._is_operator(expr):
                pass

            # Variable o número
            elif expr[self._expr_index].isalpha():
                # Variable (empieza con letra)
                j = self._expr_index
                while j < len(expr) and (expr[j].isalnum() or expr[j] == '$'):
                    j += 1
                var_name = expr[self._expr_index:j]
                
                # Determinar si es variable de string o numérica
                if var_name.endswith('$'):
                    if var_name not in self._string_vars:
                        raise ValueError(f"Variable de texto '{var_name}' no definida")
                    self._tokens.append(('STRING', self._string_vars[var_name]))
                else:
                    if var_name not in self._numeric_vars:
                        raise ValueError(f"Variable numérica '{var_name}' no definida")
                    self._tokens.append(('NUMBER', self._numeric_vars[var_name]))
                
                self._expr_index = j
            
            # Número
            elif expr[self._expr_index].isdigit():
                j = self._expr_index
                # Si es un signo negativo, avanzar
                if expr[self._expr_index] == '-':
                    j += 1
                # Leer el número
                while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                    j += 1
                num_str = expr[self._expr_index:j]
                if '.' in num_str:
                    self._tokens.append(('NUMBER', float(num_str)))
                else:
                    self._tokens.append(('NUMBER', int(num_str)))
                self._expr_index = j
            
            # Paréntesis
            elif expr[self._expr_index] == '(':
                self._tokens.append(('PAREN_OPEN', expr[self._expr_index]))
                self._expr_index += 1

            elif expr[self._expr_index] in ')':
                self._tokens.append(('PAREN_CLOSE', expr[self._expr_index]))
                self._expr_index += 1
            
            else:
                raise ValueError(f"Carácter inválido: {expr[self._expr_index]}")
        

    def _is_operator(self, expression):

        if expression[self._expr_index] == '-' and (len(self._tokens) == 0 or self._tokens[-1][0] == "PAREN_OPEN"):
            self._tokens.append(('OPERATOR', 'NEG'))
            self._expr_index += 1
            return True

        operator_candidate = ""
        for operator in self._operators:
            end_index = self._expr_index + len(operator)
            if (expression[self._expr_index: end_index] == operator 
                and len(operator_candidate) < len(operator)):
                operator_candidate = operator

        if operator_candidate:
            self._expr_index += len(operator_candidate)            
            self._tokens.append(('OPERATOR', operator_candidate))
            return True

        return False
    
    def evaluate(self, expr):
        """Evalúa la expresión usando el algoritmo Shunting Yard"""
        self._tokenize(expr)
        return self._evaluate_tokens()
    
    def _evaluate_tokens(self):
        """Evalúa los tokens usando notación postfija (RPN)"""
        output_queue = []
        operator_stack = []
        
        for token_type, token_value in self._tokens:
            if token_type in ('NUMBER', 'STRING'):
                output_queue.append(token_value)
            
            elif token_type == 'OPERATOR':
                while (operator_stack 
                    and operator_stack[-1] != '(' 
                    and ((self._operators[operator_stack[-1]].precedence 
                        > self._operators[token_value].precedence)
                        or ( self._operators[token_value].nparams == 2
                            and self._operators[operator_stack[-1]].precedence 
                                == self._operators[token_value].precedence))):
                    op = operator_stack.pop()
                    self._apply_operator(output_queue, op)

                operator_stack.append(token_value)
            
            elif token_type.startswith('PAREN'):
                if token_value == '(':
                    operator_stack.append('(')
                else:  # ')'
                    while operator_stack and operator_stack[-1] != '(':
                        self._apply_operator(output_queue, operator_stack.pop())
                    if not operator_stack:
                        raise ValueError("Paréntesis desbalanceados")
                    operator_stack.pop()  # Remover '('
        
        # Aplicar operadores restantes
        while operator_stack:
            op = operator_stack.pop()
            if op == '(':
                raise ValueError("Paréntesis desbalanceados")
            self._apply_operator(output_queue, op)
        
        if len(output_queue) != 1:
            raise ValueError("Expresión inválida")
        
        return output_queue[0]
    
    def _apply_operator(self, stack, operator):
        """Aplica un operador a los últimos dos elementos del stack""" 
        nparams = self._operators[operator].nparams
        if len(stack) < nparams:
            raise ValueError(f"Operación no válida: {operator}")
        
        if nparams == 2:

            right = stack.pop()
            left = stack.pop()

            # Operaciones con números
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                result = self._operators[operator].func(left, right)
                stack.append(result)
            
            # Operaciones con strings
            elif isinstance(left, str) and isinstance(right, str):
                if operator == '+':
                    stack.append(left + right)
                else:
                    raise ValueError(f"Operación {operator} no válida entre strings")
            
            elif isinstance(left, str) and isinstance(right, (int, float)):
                if operator == '*':
                    stack.append(left * int(right))
                else:
                    raise ValueError(f"Operación {operator} no válida entre string y número")
            
            elif isinstance(left, (int, float)) and isinstance(right, str):
                if operator == '*':
                    stack.append(right * int(left))
                else:
                    raise ValueError(f"Operación {operator} no válida entre número y string")
            
            else:
                raise ValueError("Operación no válida")

        elif nparams == 1:
            result = self._operators[operator].func(stack.pop())
            stack.append(result)

        elif nparams == 0:
            result = self._operators[operator].func()
            stack.append(result)


# Ejemplos de uso
if __name__ == "__main__":
    # Definir diccionarios de variables
    numeric_vars = {
        'x': 10,
        'y': 5,
        'pi': 3.14159,
        'edad': 25,
        'precio': 99.99
    }
    
    string_vars = {
        'nombre$': 'Juan',
        'apellido$': 'Pérez',
        'saludo$': 'Hola',
        'lenguaje$': 'Python'
    }
    
    # Crear intérprete con las variables
    interpreter = ExpressionInterpreter(numeric_vars, string_vars)
    
    test_cases = [
        # Pruebas con números negativos
        ('-2', -2),                       # -2
        ('-5 + 3', -2),                   # -5 + 3 = -2
        ('10 + (-5)', 5),                  # 10 + (-5) = 5
        ('(-2) * 3', -6),                 # -2 * 3 = -6
        ('-10 / 2', -5.0),                  # -10 / 2 = -5.0
        ('5 - (-3)', 8),                   # 5 - (-3) = 8
        
        # Operaciones con variables numéricas
        ('x + y', 15),                    # 10 + 5 = 15
        ('x * 2', 20),                    # 10 * 2 = 20
        ('(x + y) * 2', 30),              # (10 + 5) * 2 = 30
        ('precio - 10', 89.99),              # 99.99 - 10 = 89.99
        ('pi * 2', 6.28318),                   # 3.14159 * 2 = 6.28318
        
        # Operaciones con variables de texto
        ('saludo$ + " " + nombre$', "Hola Juan"),  # "Hola Juan"
        ('lenguaje$ * 3', "PythonPythonPython"),            # "PythonPythonPython"
        ('nombre$ + " " + apellido$', "Juan Pérez"),# "Juan Pérez"
        
        # Mezcla de variables y literales
        ('x + 5', 15),                    # 10 + 5 = 15
        ('(x + y) / 3', 5.0),              # 15 / 3 = 5.0
        
        # Expresiones complejas
        ('(x * 2) + (y * 3)', 35),        # 20 + 15 = 35
        ('saludo$ + ", " + nombre$ + "!"', "Hola, Juan!"),  # "Hola, Juan!"
        
        # Más pruebas con negativos
        ('(-5 + 3) * 2', -4),             # (-5 + 3) * 2 = -4
        ('x + (-y)', 5),                 # 10 + (-5) = 5
        ('x + (-3)', 7),                 # 10 + (-3) = 7

        # Booleans
        ('x < y', False),
        ('x > y', True),
        ('x >= 10 AND y = 5', True),
        ('x = 10 OR y < 5', True),
        ('x = 0 NOR y = 0', True),
        ('x < 6', False),
        ('NOT x < 6', True),
        ('NOT x < 6 AND NOT y = 7', True),

        #Math functions
        ('SQR 4 + 5', 7),
        ('SQR (4 + 5)', 3),
        ('SQR (-4 + 13)', 3),
        ('ABS (-3)', 3),
        ('SGN (-3)', -1),
        ('SGN 3', 1),
        ('SGN 0', 0),

        #String functions
        ('STR$ (10*10)', "100"),
        ('LEN STR$ 100.000', 3)
    ]
    
    print("Variables numéricas:", numeric_vars)
    print("Variables de texto:", string_vars)
    print("\n" + "=" * 60)
    print("Evaluando expresiones con variables:")
    print("=" * 60)

    for expr, expected_result in test_cases:
        try:
            result = interpreter.evaluate(expr)
            correct_message = "OK" if expected_result == result else f"; expected: {expected_result}"
            print(f"{expr:35} = {result} {correct_message}")
        except Exception as e:
            print(f"{expr:35} = ERROR: {e}")
    
    # Ejemplo interactivo
    print("\n" + "=" * 60)
    print("Prueba tus propias expresiones (escribe 'salir' para terminar):")
    print("Puedes usar las variables definidas arriba")
    print("=" * 60)
    
    while True:
        try:
            expr = input("\nExpresión: ").strip()
            if expr.lower() in ('salir', 'exit', 'quit'):
                break
            if expr:
                result = interpreter.evaluate(expr)
                print(f"Resultado: {result}")
        except Exception as e:
            print(f"Error: {e}")