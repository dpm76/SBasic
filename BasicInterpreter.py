from ExpressionInterpreter import ExpressionInterpreter
from re import split as re_split

class BasicInterpreter:
    def __init__(self):
        self._program = []          # [(line_number, code)]
        self._line_index = {}       # line_number -> index in program
        self._pc = 0                # program counter
        self._num_variables = {}
        self._str_variables = {}
        self._expr_interpreter = ExpressionInterpreter(self._num_variables, self._str_variables)
        self._stop = False
        self._return_stack = []
        self._data_buffer = []
        self._data_buffer_index = 0
        self._restore_line_index = {}
        
    def load(self, stream):
        """
        stream: iterable de líneas (archivo, lista, etc.)
        """
        self._program = []
        self._line_index = {}
        self._data_buffer = []
        self._data_buffer_index = 0
        
        for raw_line in stream:
            raw_line = raw_line.strip()
            if not raw_line:
                continue

            number_str, code = raw_line.split(" ", 1)
            code_parts = re_split(r':(?=(?:[^"]*"[^"]*")*[^"]*$)', code)
            part_index = 0
            number = int(number_str)
            for code_part in code_parts:
                code_part = code_part.strip()
                if code_part.startswith("DATA"):
                    self.execute_data(number, code_part)
                else:
                    self._program.append((number, part_index, code_part))                
                    part_index += 1

        # ordenar por número de línea
        self._program.sort(key=lambda x: (x[0], x[1]))

        # crear índice rápido para GOTO
        for idx, (line_number, _, _) in enumerate(self._program):
            if not line_number in self._line_index:
                self._line_index[line_number] = idx

        print(self._data_buffer)
        print(self._restore_line_index)

    def run(self, line=0):
        self._pc = 0 if line == 0 else self._line_index[line]
        self._stop = False
        self._return_stack = []
        self._data_buffer_index = 0

        try:
            while not self._stop and self._pc < len(self._program):
                line_number, _, code = self._program[self._pc]
                self.execute_sentence(code)
                self._pc += 1
            if self._stop:
                print("\r\nProgram stop")
            else:
                print("\r\nOK")
        except (ValueError, RuntimeError) as re:
            print(f"\r\nError: {re}\r\n\tat line {line_number} {code}")
        except KeyboardInterrupt:
            print("\r\nInterrupted program")

    def execute_sentence(self, code):
        code = code.strip()
        code_upper = code.upper()

        if code_upper.startswith("PRINT"):
            self.execute_print(code)

        elif code_upper.startswith("GO TO") or code_upper.startswith("GOTO"):
            self.execute_goto(code)

        elif code_upper.startswith("LET"):
            self.execute_let(code)

        elif code_upper.startswith("IF"):
            self.execute_if(code)

        elif code_upper.startswith("INPUT"):
            self.execute_input(code)

        elif code_upper.startswith("FOR"):
            self.execute_for(code)

        elif code_upper.startswith("NEXT"):
            self.execute_next(code)

        elif code_upper.startswith("REM"):
            self.execute_rem(code)

        elif code_upper.startswith("STOP"):
            self.execute_stop(code)

        elif code_upper.startswith("GO SUB") or code_upper.startswith("GOSUB"):
            self.execute_gosub(code)

        elif code_upper.startswith("RETURN"):
            self.execute_return(code)

        elif code_upper.startswith("READ"):
            self.execute_read(code)

        elif code_upper.startswith("RESTORE"):
            self.execute_restore(code)

        else:
            raise RuntimeError(f"Unknown keyword: {code}")

    def execute_print(self, code):
        if code == "PRINT":
            print()
            return

        _, rest = code.split(" ", 1)
        rest = rest.strip()
        args = re_split(r';(?=(?:[^"]*"[^"]*")*[^"]*$)', rest)

        for arg in args:
            if arg.startswith('"') and arg.endswith('"'):
                print(arg[1:-1], end="")
            elif arg != "":
                value = self._expr_interpreter.evaluate(arg)
                if isinstance(value, str):
                    print(value, end="")
                else:
                    print(f"{value:g}", end="")

        if not code.endswith(";"):
            print()

    def execute_goto(self, code):
        # GO TO 10
        parts = code.split()
        target_line = int(parts[-1])

        if target_line not in self._line_index:
            raise RuntimeError(f"Undefined line number {target_line}")

        # -1 porque el loop principal hará pc += 1
        self._pc = self._line_index[target_line] - 1

    def execute_let(self, code):
        _, rest = code.split(" ", 1)
        var, expr = rest.split("=", 1)

        var = var.strip()
        expr = expr.strip()
        
        self._assignVariable(var, expr)

    def _assignVariable(self, var_name, expression_value):
        value = self._expr_interpreter.evaluate(expression_value)
        if var_name.endswith("$"):
            if not isinstance(value, str):
                raise RuntimeError("Type mismatch. A string was expected.")
            self._str_variables[var_name] = value
        else:
            if not isinstance(value, (int, float)):
                raise RuntimeError("Type mismatch. A number was expected.")
            self._num_variables[var_name] = value

    def execute_if(self, code):

        _, rest = code.split(" ", 1)
        condition, then = rest.split(" THEN ", 1)
        if self._expr_interpreter.evaluate(condition.strip()) != 0:
            self.execute_sentence(then.strip())

    def execute_input(self, code):

        _, rest = code.split(" ", 1)
        chunks = re_split(r';(?=(?:[^"]*"[^"]*")*[^"]*$)', rest, 1)
        if len(chunks) > 1:
            prompt = chunks[0]
            variable = chunks[1]
            value = input(prompt.strip()[1:-1])
        else:
            variable = chunks[0]
            value = input("? ")
        variable = variable.strip()
        if variable.endswith("$"):
            self._str_variables[variable] = value
        else:
            self._num_variables[variable] = float(value)

    def execute_for(self, code):
        _, rest = code.split(" ", 1)
        loop_variable, rest = rest.split("=", 1)
        loop_init, rest = rest.strip().split("TO", 1)
        loop_variable = loop_variable.strip()
        
        if "STEP" in rest:
            loop_end, loop_step = rest.strip().split("STEP")
        else:
            loop_end = rest.strip()
            loop_step = "1"

        self._num_variables[loop_variable] = self._expr_interpreter.evaluate(loop_init.strip())
        self._num_variables[f"for_end_{loop_variable}"] = self._expr_interpreter.evaluate(loop_end.strip())
        self._num_variables[f"for_step_{loop_variable}"] = self._expr_interpreter.evaluate(loop_step.strip())
        self._num_variables[f"for_num_codeline_{loop_variable}"] = self._pc

        if self._num_variables[f"for_step_{loop_variable}"] == 0:
            raise ValueError("FOR STEP can not be 0.")

    def execute_next(self, code):

        _, loop_variable = code.split(" ", 1)
        
        step = self._num_variables[f"for_step_{loop_variable}"]
        self._num_variables[loop_variable] += step
        if (step > 0 and self._num_variables[loop_variable] <= self._num_variables[f"for_end_{loop_variable}"]) \
            or ( step < 0 and self._num_variables[loop_variable] >= self._num_variables[f"for_end_{loop_variable}"]):
            self._pc = self._num_variables[f"for_num_codeline_{loop_variable}"]

    def execute_rem(self, code):
        pass #Do nothing

    def execute_stop(self, code):
        self._stop = True

    def execute_gosub(self, code):
        self._return_stack.append(self._pc)
        parts = code.split()
        target_line = int(parts[-1])
        self._pc = self._line_index[target_line] - 1

    def execute_return(self, code):
        self._pc = self._return_stack.pop()

    def execute_data(self, line_number, code):
        if not line_number in self._restore_line_index:
            self._restore_line_index[line_number] = len(self._data_buffer)

        _, row_data = code.split(" ", 1)        
        for data_element in row_data.split(","):
            data_element = data_element.strip()
            self._data_buffer.append(data_element)

    def execute_read(self, code):
        _, params = code.split(" ", 1)
        var_names = params.split(",")
        for var_name in var_names:
            if self._data_buffer_index == len(self._data_buffer):
                raise RuntimeError("End of data")
            var_name = var_name.strip()            
            value = self._data_buffer[self._data_buffer_index]
            self._assignVariable(var_name, value)
            self._data_buffer_index += 1

    def execute_restore(self, code):
        items = code.split(" ")        
        self._data_buffer_index = self._restore_line_index[int(items[-1])] if len(items) > 1 else 0
        