import re

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
        
        self._operators = {
            '^': {'precedence': 2, 'func': lambda a, b: a ** b},
            '+': {'precedence': 1, 'func': lambda a, b: a + b},
            '-': {'precedence': 1, 'func': lambda a, b: a - b},
            '*': {'precedence': 2, 'func': lambda a, b: a * b},
            '/': {'precedence': 2, 'func': lambda a, b: a / b if b != 0 else (_ for _ in ()).throw(ValueError("Zero division"))},
            '>': {'precedence': 0, 'func': lambda a, b: a > b},
            '<': {'precedence': 0, 'func': lambda a, b: a < b},
            '=': {'precedence': 0, 'func': lambda a, b: a == b},
            '<=': {'precedence': 0, 'func': lambda a, b: a <= b},
            '=<': {'precedence': 0, 'func': lambda a, b: a <= b},
            '>=': {'precedence': 0, 'func': lambda a, b: a >= b},
            '=>': {'precedence': 0, 'func': lambda a, b: a >= b},
            '<>': {'precedence': 0, 'func': lambda a, b: a != b},
        }
    
    def _tokenize(self, expr):
        """Convierte la expresión en tokens"""
        expr = expr.strip()
        tokens = []
        i = 0
        
        while i < len(expr):
            # Saltar espacios
            if expr[i].isspace():
                i += 1
                continue
            
            # String entre comillas
            if expr[i] == '"':
                j = i + 1
                while j < len(expr) and expr[j] != '"':
                    j += 1
                if j >= len(expr):
                    raise ValueError("String sin cerrar")
                tokens.append(('STRING', expr[i+1:j]))
                i = j + 1
            
            # Variable o número
            elif expr[i].isalpha():
                # Variable (empieza con letra)
                j = i
                while j < len(expr) and (expr[j].isalnum() or expr[j] == '$'):
                    j += 1
                var_name = expr[i:j]
                
                # Determinar si es variable de string o numérica
                if var_name.endswith('$'):
                    if var_name not in self._string_vars:
                        raise ValueError(f"Variable de texto '{var_name}' no definida")
                    tokens.append(('STRING', self._string_vars[var_name]))
                else:
                    if var_name not in self._numeric_vars:
                        raise ValueError(f"Variable numérica '{var_name}' no definida")
                    tokens.append(('NUMBER', self._numeric_vars[var_name]))
                
                i = j
            
            # Número (incluyendo negativos)
            elif expr[i].isdigit() or (expr[i] == '-' and self._is_negative_number(tokens, expr, i)):
                j = i
                # Si es un signo negativo, avanzar
                if expr[i] == '-':
                    j += 1
                # Leer el número
                while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                    j += 1
                num_str = expr[i:j]
                if '.' in num_str:
                    tokens.append(('NUMBER', float(num_str)))
                else:
                    tokens.append(('NUMBER', int(num_str)))
                i = j
            
            # Operador
            elif expr[i] in '^+-*/<>=':
                operator = expr[i]                
                i += 1
                if i < len(expr) and expr[i] in '=<>':
                    operator += expr[i]
                    i += 1

                tokens.append(('OPERATOR', operator))
            
            # Paréntesis
            elif expr[i] in '()':
                tokens.append(('PAREN', expr[i]))
                i += 1
            
            else:
                raise ValueError(f"Carácter inválido: {expr[i]}")
        
        return tokens
    
    def _is_negative_number(self, tokens, expr, pos):
        """
        Determina si un '-' es parte de un número negativo o un operador de resta.
        Es un número negativo si:
        - Es el primer token, O
        - El token anterior es un operador, O
        - El token anterior es un paréntesis de apertura '('
        Y además hay un dígito después del '-'
        """
        # Verificar que hay un dígito después del '-'
        if pos + 1 >= len(expr) or not expr[pos + 1].isdigit():
            return False
        
        # Si no hay tokens previos, es un número negativo
        if not tokens:
            return True
        
        # Obtener el último token
        last_token_type, last_token_value = tokens[-1]
        
        # Es número negativo si viene después de un operador o paréntesis de apertura
        if last_token_type == 'OPERATOR':
            return True
        if last_token_type == 'PAREN' and last_token_value == '(':
            return True
        
        return False
    
    def evaluate(self, expr):
        """Evalúa la expresión usando el algoritmo Shunting Yard"""
        tokens = self._tokenize(expr)
        return self._evaluate_tokens(tokens)
    
    def _evaluate_tokens(self, tokens):
        """Evalúa los tokens usando notación postfija (RPN)"""
        output_queue = []
        operator_stack = []
        
        for token_type, token_value in tokens:
            if token_type in ('NUMBER', 'STRING'):
                output_queue.append(token_value)
            
            elif token_type == 'OPERATOR':
                while (operator_stack and 
                       operator_stack[-1] != '(' and
                       self._operators[operator_stack[-1]]['precedence'] >= 
                       self._operators[token_value]['precedence']):
                    self._apply_operator(output_queue, operator_stack.pop())
                operator_stack.append(token_value)
            
            elif token_type == 'PAREN':
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
        if len(stack) < 2:
            raise ValueError("Expresión inválida")
        
        right = stack.pop()
        left = stack.pop()
        
        # Operaciones con números
        if isinstance(left, (int, float)) and isinstance(right, (int, float)):
            result = self._operators[operator]['func'](left, right)
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
        '-2',                       # -2
        '-5 + 3',                   # -5 + 3 = -2
        '10 + -5',                  # 10 + (-5) = 5
        '(-2) * 3',                 # -2 * 3 = -6
        '-10 / 2',                  # -10 / 2 = -5.0
        '5 - -3',                   # 5 - (-3) = 8
        
        # Operaciones con variables numéricas
        'x + y',                    # 10 + 5 = 15
        'x * 2',                    # 10 * 2 = 20
        '(x + y) * 2',              # (10 + 5) * 2 = 30
        'precio - 10',              # 99.99 - 10 = 89.99
        'pi * 2',                   # 3.14159 * 2 = 6.28318
        
        # Operaciones con variables de texto
        'saludo$ + " " + nombre$',  # "Hola Juan"
        'lenguaje$ * 3',            # "PythonPythonPython"
        'nombre$ + " " + apellido$',# "Juan Pérez"
        
        # Mezcla de variables y literales
        'x + 5',                    # 10 + 5 = 15
        '(x + y) / 3',              # 15 / 3 = 5.0
        
        # Expresiones complejas
        '(x * 2) + (y * 3)',        # 20 + 15 = 35
        'saludo$ + ", " + nombre$ + "!"',  # "Hola, Juan!"
        
        # Más pruebas con negativos
        '(-5 + 3) * 2',             # (-5 + 3) * 2 = -4
        'x + -y',                   # 10 + (-5) = 5
    ]
    
    print("Variables numéricas:", numeric_vars)
    print("Variables de texto:", string_vars)
    print("\n" + "=" * 60)
    print("Evaluando expresiones con variables:")
    print("=" * 60)
    
    for expr in test_cases:
        try:
            result = interpreter.evaluate(expr)
            print(f"{expr:35} = {result}")
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