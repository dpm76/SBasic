from ExpressionInterpreter import ExpressionInterpreter
from re import split as re_split

class BasicInterpreter:
    def __init__(self):
        self.program = []          # [(line_number, code)]
        self.line_index = {}       # line_number -> index in program
        self.pc = 0                # program counter
        self.num_variables = {}
        self.str_variables = {}
        self._expr_interpreter = ExpressionInterpreter(self.num_variables, self.str_variables)
        self._stop = False
        
    def load(self, stream):
        """
        stream: iterable de líneas (archivo, lista, etc.)
        """
        self.program = []
        self.line_index = {}
        
        for raw_line in stream:
            raw_line = raw_line.strip()
            if not raw_line:
                continue

            number, code = raw_line.split(" ", 1)
            code_parts = re_split(r':(?=(?:[^"]*"[^"]*")*[^"]*$)', code)
            part_index = 0
            for code_part in code_parts:
                self.program.append((int(number), part_index, code_part.strip()))
                part_index += 1

        # ordenar por número de línea
        self.program.sort(key=lambda x: (x[0], x[1]))

        # crear índice rápido para GOTO
        for idx, (line_number, _, _) in enumerate(self.program):
            if not line_number in self.line_index:
                self.line_index[line_number] = idx

    def run(self, line=0):
        self.pc = 0 if line == 0 else self.line_index[line]
        self._stop = False
        try:
            while not self._stop and self.pc < len(self.program):
                line_number, _, code = self.program[self.pc]
                self.execute_sentence(code)
                self.pc += 1
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

        else:
            raise RuntimeError(f"Unknown keyword: {code}")

    def execute_print(self, code):
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
        parts = code.upper().split()
        target_line = int(parts[-1])

        if target_line not in self.line_index:
            raise RuntimeError(f"Undefined line number {target_line}")

        # -1 porque el loop principal hará pc += 1
        self.pc = self.line_index[target_line] - 1

    def execute_let(self, code):
        # LET A$ = "HOLA"
        _, rest = code.split(" ", 1)
        var, expr = rest.split("=", 1)

        var = var.strip()
        expr = expr.strip()

        value = self._expr_interpreter.evaluate(expr)

        if var.endswith("$"):
            if not isinstance(value, str):
                raise RuntimeError("Type mismatch")
            self.str_variables[var] = value
        else:
            if not isinstance(value, (int, float)):
                raise RuntimeError("Type mismatch")
            self.num_variables[var] = value

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
            self.str_variables[variable] = value
        else:
            self.num_variables[variable] = float(value)

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

        self.num_variables[loop_variable] = self._expr_interpreter.evaluate(loop_init.strip())
        self.num_variables[f"for_end_{loop_variable}"] = self._expr_interpreter.evaluate(loop_end.strip())
        self.num_variables[f"for_step_{loop_variable}"] = self._expr_interpreter.evaluate(loop_step.strip())
        self.num_variables[f"for_num_codeline_{loop_variable}"] = self.pc

        if self.num_variables[f"for_step_{loop_variable}"] == 0:
            raise ValueError("FOR STEP can not be 0.")

    def execute_next(self, code):

        _, loop_variable = code.split(" ", 1)
        
        step = self.num_variables[f"for_step_{loop_variable}"]
        self.num_variables[loop_variable] += step
        if (step > 0 and self.num_variables[loop_variable] <= self.num_variables[f"for_end_{loop_variable}"]) \
            or ( step < 0 and self.num_variables[loop_variable] >= self.num_variables[f"for_end_{loop_variable}"]):
            self.pc = self.num_variables[f"for_num_codeline_{loop_variable}"]

    def execute_rem(self, code):
        pass #Do nothing

    def execute_stop(self, code):
        self._stop = True
    
    
