# Sinclair BASIC Interpreter (SBasic)

This project is a **Sinclair BASIC–inspired interpreter**, written in **Python**.  
It is mainly based on the BASIC dialect used by the **ZX Spectrum**, with special attention to the **ZX Spectrum +2**.

The project focuses on interpreting the **language itself**, not on emulating the original hardware.  
It is currently a **command-line interpreter**, with future plans for graphical and web-based environments.

---

## 🎯 Purpose of the Project

The main purpose of this project is **educational, experimental, and preservational**.

In particular, it aims to:

- Understand how an **interpreted programming language** works internally
- Explore classic language design decisions and their historical constraints
- Preserve the spirit of Sinclair BASIC in a modern and readable implementation
- Serve as a base for future extensions such as graphical output and interactive environments

This project is **not intended for production use**.

---

## 💡 Motivation

For many people, BASIC was their **first programming language**.  
Its simplicity, combined with its particular design choices, makes it an excellent subject for studying how programming languages work at a fundamental level.

Implementing a Sinclair BASIC interpreter today allows:

- Learning language implementation from first principles
- Comparing early home-computer languages with modern programming models
- Experimenting without large frameworks or complex dependencies
- Writing software for understanding, curiosity, and enjoyment

---

## 🕹️ Why ZX Spectrum +2?

The ZX Spectrum +2 was the computer on which I first started programming.

It was not only my introduction to BASIC, but also my first direct experience with how a computer behaves when you type code, make mistakes, and immediately see the results. Writing programs on the ZX Spectrum +2 meant working close to the machine, with very little abstraction and very clear feedback.

Choosing the ZX Spectrum +2 as a reference for this interpreter is therefore both a **technical and a personal decision**:

- It represents a well-defined and historically significant version of BASIC
- Its dialect is simple, expressive, and full of characteristic design choices
- It encourages structured thinking using minimal constructs
- It reflects a time when learning to program meant understanding control flow, state, and execution order very explicitly

Rather than aiming for perfect emulation, this project tries to **capture the feel and logic** of programming on a ZX Spectrum +2 — and other computers of these days — while implementing it in a modern, readable, and extensible way.

In that sense, this interpreter is not only a technical exercise, but also a way of revisiting — and better understanding — the environment where my interest in programming began.

---

## 🖥️ Current Usage (CLI)

At its current stage, the interpreter is executed from the command line.

### Invocation

```bash
python3 SBasicCLI.py <program-filepath>
```

Where `<program-filepath>` is a text file containing a BASIC program with line numbers.

The program is executed in **text mode**, and all output is displayed directly in the terminal.

---

## ⚙️ Current Features

The interpreter implements a **small but functional subset of BASIC**.

### Language Model

- Line-numbered programs
- Sequential execution with a program counter
- Implicit typing:
  - numeric variables (`a`, `total`)
  - string variables ending in `$` (`a$`, `n$`)
- Basic error handling

### Implemented Keywords

- `PRINT`
- `GOTO` / `GO TO`
- `GOSUB` / `GO SUB` - `RETURN`
- `LET`
  - numeric variable assignment
  - string variable assignment
- `IF ... THEN`
- `INPUT`
- `FOR` - `NEXT`
- `STOP`
- `REM`
- `DATA`, `READ`, `RESTORE`
- `AND`, `OR`, `NOR`, `NOT`
- `RANDOMIZE` / `RND`
- `COS`, `SIN`, `TAN`, `ACS`, `ASN`, `ATN` and `PI` constant
- `LN`, `EXP`
- `SQR`
- `ABS`
- `INT`
- `SGN`
- `STR$`
- `LEN` 

### Expression Evaluation

The interpreter supports basic expression evaluation, including:

- Arithmetic operators: `+`, `-`, `*`, `/`
- Power operator: `^`
- Comparison operators: `<`, `<=`, `=`, `>=`, `>`
- Parenthesized expressions

Expressions can be used in assignments, conditions, and `PRINT` statements.

---

## 🏗️ Internal Architecture (Draft)

The interpreter is intentionally designed with a **simple and readable internal architecture**, prioritizing clarity over performance or full compatibility.

At a high level, the execution pipeline is:

```
BASIC source code (text)
        ↓
Line loader and sorter
        ↓
Parser / dispatcher
        ↓
Expression evaluator
        ↓
Execution engine
```

### Main Components

- **Program Loader**
  - Reads the BASIC program from a text stream
  - Extracts line numbers and source code
  - Sorts lines numerically
  - Builds a line-number-to-index map for fast `GOTO` resolution

- **Execution Engine**
  - Maintains a program counter
  - Executes the program line by line
  - Dispatches each line to the corresponding keyword handler
  - Controls flow instructions such as `GOTO`, `IF`, `FOR/NEXT`, and `STOP`

- **Variable Storage**
  - Numeric variables and string variables are stored separately
  - String variables follow the Sinclair BASIC convention of ending with `$`
  - Typing is implicit and determined by variable name

- **Expression Evaluator**
  - Evaluates arithmetic and comparison expressions
  - Supports operator precedence and parentheses
  - Performs basic translation from BASIC syntax to Python-compatible syntax
  - Designed to remain simple and easy to replace or extend

- **Input / Output Layer**
  - Currently implemented using standard input/output (terminal)
  - Output is produced incrementally, statement by statement
  - Designed to be decoupled from the execution engine to allow future
    graphical or web-based frontends

### Design Philosophy

- Keep each component small and understandable
- Avoid premature abstraction
- Favor explicit logic over clever optimizations
- Make the interpreter easy to extend step by step

This architecture is still evolving and will likely be refactored as new
features are added.

---

## 📘 BASIC Dialect Documentation (Draft)

The implemented BASIC dialect aims to be **as close as reasonably possible to Sinclair BASIC for the ZX Spectrum +2**, while still allowing internal simplicity and incremental development.

The goal is **behavioral similarity**, not perfect compatibility.

### General Characteristics

- Programs consist of **numbered lines**
- Lines are executed in ascending numerical order
- Execution flow can be altered using control statements
- Variables are created implicitly on first assignment
- Keywords are case-insensitive
- Whitespace is generally not significant

### Variables

- **Numeric variables**
  - Examples: `a`, `x`, `total`
  - Stored as numeric values
- **String variables**
  - Must end with `$`
  - Examples: `a$`, `n$`

The variable naming rules and `$` suffix follow the Sinclair BASIC convention.

### Supported Statements

#### `PRINT`

Prints values to the output.

Examples:
```
PRINT "Hello"
PRINT a
PRINT "VALUE: "; a$
```

#### `LET`

Assigns values to variables.

Examples:
```
LET a = 10
LET n$ = "SINCLAIR"
LET a = a + 1
```

#### `GOTO` / `GO TO`

Jumps unconditionally to the specified line number.

Example:
```
GOTO 100
```

#### `IF`

Conditional execution.

Example:
```
IF a > 10 THEN GOTO 200
```

#### `INPUT`

Reads a value from standard input.

Examples:
```
INPUT a
INPUT n$
INPUT "Enter a number: "; a
INPUT "What's your name? "; n$
```

#### `FOR` / `NEXT`

Looping construct.

Example:
```
FOR I = 1 TO 10
PRINT I
NEXT I
```

#### `STOP`

Stops program execution immediately.

#### `REM`

Comment line. Ignored during execution.

Example:
```
REM This is a comment
```

#### Multiple keywords in the same line

Using colon `:` can join several instructions in the same line.

Example:
```
10 FOR n = 1 TO 10 : PRINT n*2 : NEXT n : REM This is a for-next loop in a single line
```

---

### Expressions

Expressions support:

- Arithmetic operators: `+`, `-`, `*`, `/`
- Power operator: `^`
- Comparison operators: `<`, `<=`, `=`, `>=`, `>`
- Parentheses for grouping

Examples:
```
10 LET a = (5 + 3) * 2
20 IF a >= 10 THEN PRINT a
```

### Compatibility Notes

- The dialect is inspired by **ZX Spectrum +2 Sinclair BASIC**
- Some behaviors may differ for simplicity or clarity
- Error messages are simpler than the original Spectrum messages
- Not all keywords or edge cases are implemented

This documentation is a **living document** and will be updated as the
interpreter evolves.

---

## 🚧 Known Limitations

This project does **not** aim for full Sinclair BASIC compatibility.

Current limitations include:

- No graphics (`PLOT`, `DRAW`, etc.) at this stage
- No sound support
- No hardware or memory emulation
- No binary tokenization (text-based BASIC only)
- Limited error messages compared to the original Spectrum
- Expression evaluation is intentionally simple
- Performance is not optimized

Some behaviors may differ from original Sinclair BASIC where clarity or simplicity is preferred.

---

## 🧩 Future Development

This is a **work-in-progress project** that will evolve incrementally.

Planned or possible future extensions include:

- Graphical output commands (`PLOT`, `DRAW`, etc.)
- A cross-platform graphical environment using **tkinter**
- Improved error reporting (closer to Spectrum-style messages)
- Step-by-step execution and tracing
- Cleaner separation between parsing, evaluation, and execution
- Documentation of the implemented BASIC dialect
- A future web-based interface once the interpreter core is more mature

---

## 📜 Final Note

This project exists because **not all software needs to be useful to be valuable**.

Some projects are worth building simply because they help us understand where programming languages come from, how they work internally, and why certain ideas from early computing are still relevant today.

