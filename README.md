# Mini C Compiler — Phase 1 & 2
**Lexical Analysis + Syntax Analysis with Parse Tree**

A complete two-phase compiler front-end for a C subset, implemented in
pure Python.

---

## Files

| File | Purpose |
|------|---------|
| `lexer.py` | Phase 1 — DFA-style C lexer (tokenizer) |
| `parser.py` | Phase 2 — Recursive-descent parser + parse-tree builder |
| `tk_app.py` | Tkinter GUI — run this to use the compiler interactively |
| `cli_test.py` | CLI test runner — tests all 21 programs without a GUI |

---

## How to Run

### GUI (Tkinter)
```bash
python tk_app.py
```
- Select any of the 21 programs from the dropdown
- Click **▶ Compile**
- View tokens, symbol table, text parse tree, and visual parse tree

### CLI test (all 21 programs)
```bash
python cli_test.py
```

### CLI — compile a specific file
```bash
python cli_test.py yourfile.c
python cli_test.py --tree yourfile.c     # also shows the parse tree
```

---

## Features

### Phase 1 — Lexical Analysis
- Tokenises all C constructs: keywords, identifiers, integer/float constants,
  char literals, string literals, all operators (`++`, `--`, `+=`, `||`, `&&`, …),
  brackets, punctuation, preprocessor `#include`
- Colour-coded token table in the GUI
- Symbol table (unique identifiers and constants with first-seen line)
- Lexical error reporting (illegal characters, unterminated strings)

### Phase 2 — Syntax Analysis
- Full recursive-descent parser (no external libraries)
- Handles the complete C subset used in the 21 sample programs:
  - `#include` directives
  - Function definitions with parameter lists
  - Local variable declarations with initialisers and multiple declarators
  - `if / else if / else` (any depth of nesting)
  - `for`, `while`, `do-while` loops (nested)
  - `return`, `break`, `continue`
  - All expressions: assignment, logical `&&`/`||`, relational, arithmetic,
    unary `!`/`-`/`++`/`--`, postfix `++`/`--`, function calls, subscripts
- Generates a correct labelled parse tree for every valid program
- Clear error messages with line numbers

### GUI tabs
1. **Phase 1 — Tokens** — full token table with colour-coded rows
2. **Symbol Table** — unique identifiers/constants and their first line
3. **Phase 2 — Parse Tree (text)** — ASCII tree view
4. **Parse Tree (visual)** — scrollable canvas tree with zoom buttons
5. **Grammar** — the formal grammar used by the parser

---

## Grammar Summary

```
program          -> include_list  translation_unit
translation_unit -> (func_def | global_decl)*
func_def         -> type id '(' param_list ')' compound_stmt
compound_stmt    -> '{' block_item_list '}'
block_item       -> local_decl | stmt
stmt             -> if_stmt | while_stmt | for_stmt | do_while_stmt
                  | return_stmt | break_stmt | continue_stmt
                  | compound_stmt | expr_stmt
expr             -> assign_expr (',' assign_expr)*
assign_expr      -> or_expr (assign_op assign_expr)?
or_expr          -> and_expr ('||' and_expr)*
and_expr         -> rel_expr ('&&' rel_expr)*
rel_expr         -> add_expr (relop add_expr)*
add_expr         -> mul_expr (('+' | '-') mul_expr)*
mul_expr         -> unary_expr (('*' | '/' | '%') unary_expr)*
unary_expr       -> ('!' | '-' | '++' | '--') unary_expr | postfix_expr
postfix_expr     -> primary_expr ('++'|'--'|'[' expr ']'|'(' arg_list ')')*
primary_expr     -> id | CONST | STRING | '(' expr ')'
```

---

## Requirements
- Python 3.10+
- `tkinter` (included in standard Python installations)
- No other external packages needed
