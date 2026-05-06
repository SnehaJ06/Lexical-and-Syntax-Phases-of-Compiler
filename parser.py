"""
Phase 2: Syntax Analyzer — Recursive-Descent Parser
=====================================================
Grammar (handles the full C subset in the 21 sample programs):

  program      -> include_list translation_unit
  include_list -> ('#' 'include' STRING)* | ε
  translation_unit -> (func_def | global_decl)*

  func_def     -> type id '(' param_list ')' compound_stmt
  param_list   -> ε | 'void' | param (',' param)*
  param        -> type id ('[' ']')?

  compound_stmt -> '{' block_item_list '}'
  block_item_list -> block_item* | ε
  block_item   -> stmt | local_decl

  local_decl   -> type declarator_list ';'
  declarator_list -> declarator (',' declarator)*
  declarator   -> id ('=' expr)? | id '[' expr ']'

  stmt         -> expr_stmt
               | compound_stmt
               | if_stmt
               | while_stmt
               | for_stmt
               | do_while_stmt
               | return_stmt
               | break_stmt
               | continue_stmt

  if_stmt      -> 'if' '(' expr ')' stmt ('else' stmt)?
  while_stmt   -> 'while' '(' expr ')' stmt
  for_stmt     -> 'for' '(' for_init expr? ';' expr? ')' stmt
  for_init     -> local_decl | expr_stmt
  do_while_stmt-> 'do' compound_stmt 'while' '(' expr ')' ';'
  return_stmt  -> 'return' expr? ';'
  break_stmt   -> 'break' ';'
  continue_stmt-> 'continue' ';'
  expr_stmt    -> expr? ';'

  expr         -> assign_expr (',' assign_expr)*
  assign_expr  -> unary_expr assign_op assign_expr | cond_expr
  assign_op    -> '=' | '+=' | '-=' | '*=' | '/='
  cond_expr    -> or_expr

  or_expr      -> and_expr ('||' and_expr)*
  and_expr     -> rel_expr ('&&' rel_expr)*
  rel_expr     -> add_expr (('<'|'>'|'<='|'>='|'=='|'!=') add_expr)*
  add_expr     -> mul_expr (('+' | '-') mul_expr)*
  mul_expr     -> unary_expr (('*' | '/' | '%') unary_expr)*
  unary_expr   -> ('!'|'-'|'++'|'--') unary_expr | postfix_expr
  postfix_expr -> primary_expr ('++'|'--'|'['expr']'|'('arg_list')')*
  primary_expr -> id | CONSTANT | STRING | '(' expr ')' | sizeof_expr
  sizeof_expr  -> 'sizeof' '(' type_or_expr ')'
  arg_list     -> ε | expr (',' expr)*
"""

from lexer import tokenize, Token


# ─────────────────────────────── AST Node ────────────────────────────────────
class Node:
    """Generic parse-tree node."""
    __slots__ = ("label", "children")

    def __init__(self, label: str):
        self.label = label
        self.children: list["Node"] = []

    def add(self, child):
        if child is not None:
            self.children.append(child)
        return child

    def leaf(label: str) -> "Node":          # static helper
        return Node(label)
    leaf = staticmethod(leaf)


# ──────────────────────────────── Error ──────────────────────────────────────
class ParseError(Exception):
    pass


# ──────────────────────────────── Parser ─────────────────────────────────────
class Parser:
    def __init__(self, tokens: list[Token]):
        # Filter out HASH tokens used for preprocessor — we handle
        # #include in the grammar; skip bare HASH + path already included
        self.tokens = [t for t in tokens
                       if t.type not in ("HASH",)]
        # But we need to keep include / string tokens for #include parsing;
        # actually we already pre-filtered in tokenize, so keep all non-HASH.
        self.pos = 0
        self._errors: list[str] = []

    # ── token stream helpers ──────────────────────────────────────────────
    def peek(self, offset=0) -> Token | None:
        idx = self.pos + offset
        return self.tokens[idx] if idx < len(self.tokens) else None

    def at_end(self) -> bool:
        return self.pos >= len(self.tokens)

    def check(self, lexeme=None, ttype=None) -> bool:
        t = self.peek()
        if t is None:
            return False
        if lexeme is not None and t.lexeme != lexeme:
            return False
        if ttype is not None and t.type != ttype:
            return False
        return True

    def eat(self, lexeme=None, ttype=None) -> Token:
        t = self.peek()
        if t is None:
            raise ParseError(
                f"Unexpected end of input"
                + (f", expected '{lexeme}'" if lexeme else "")
            )
        if lexeme is not None and t.lexeme != lexeme:
            raise ParseError(
                f"Line {t.line}: expected '{lexeme}', got '{t.lexeme}'"
            )
        if ttype is not None and t.type != ttype:
            raise ParseError(
                f"Line {t.line}: expected {ttype}, got '{t.lexeme}'"
            )
        self.pos += 1
        return t

    def match(self, *lexemes) -> Token | None:
        t = self.peek()
        if t and t.lexeme in lexemes:
            self.pos += 1
            return t
        return None

    def match_type(self, *ttypes) -> Token | None:
        t = self.peek()
        if t and t.type in ttypes:
            self.pos += 1
            return t
        return None

    def is_type_kw(self, tok: Token | None = None) -> bool:
        kw = (tok or self.peek())
        TYPE_KWS = {"int", "float", "char", "double", "void", "long",
                    "short", "unsigned", "signed", "struct"}
        return kw is not None and kw.type == "KEYWORD" and kw.lexeme in TYPE_KWS

    def leaf(self, text: str) -> Node:
        return Node(text)

    # ── TOP LEVEL ─────────────────────────────────────────────────────────
    def parse_program(self) -> Node:
        root = Node("program")
        root.add(self.parse_include_list())
        root.add(self.parse_translation_unit())
        if not self.at_end():
            t = self.peek()
            raise ParseError(
                f"Line {t.line}: unexpected token '{t.lexeme}' at top level"
            )
        return root

    def parse_include_list(self) -> Node:
        node = Node("include_list")
        while self.check(ttype="HASH") or (
            self.check(ttype="KEYWORD") and
            self.peek() and self.peek().lexeme == "include"
        ):
            inc = Node("include_directive")
            # could be HASH already consumed; or starts with 'include'
            if self.check(ttype="HASH"):
                h = self.eat()
                inc.add(self.leaf(h.lexeme))
            if self.check("include"):
                kw = self.eat()
                inc.add(self.leaf(kw.lexeme))
            # consume the header
            if self.check(ttype="STRING_LITERAL"):
                s = self.eat()
                inc.add(self.leaf(s.lexeme))
            node.add(inc)
        if not node.children:
            node.add(self.leaf("ε"))
        return node

    def parse_translation_unit(self) -> Node:
        node = Node("translation_unit")
        while not self.at_end():
            # Could be func_def or global_decl; peek ahead
            if self._looks_like_func_def():
                node.add(self.parse_func_def())
            elif self.is_type_kw():
                node.add(self.parse_global_decl())
            else:
                # bare statement at top level (e.g. some snippet programs)
                node.add(self.parse_stmt())
        if not node.children:
            node.add(self.leaf("ε"))
        return node

    def _looks_like_func_def(self) -> bool:
        """Peek ahead to decide: type id ( ..."""
        if not self.is_type_kw():
            return False
        # offset 1: should be id
        t1 = self.peek(1)
        if t1 is None:
            return False
        # offset 2: should be '('
        t2 = self.peek(2)
        if t2 is not None and t2.lexeme == "(":
            return True
        # pointer type: int *func(
        if t1 and t1.lexeme == "*":
            t3 = self.peek(3)
            return t3 is not None and t3.lexeme == "("
        return False

    # ── GLOBAL DECL (top-level variable) ─────────────────────────────────
    def parse_global_decl(self) -> Node:
        node = Node("global_decl")
        type_tok = self.eat(ttype="KEYWORD")
        node.add(self.leaf(type_tok.lexeme))
        node.add(self.parse_declarator_list())
        self.eat(";"); node.add(self.leaf(";"))
        return node

    # ── FUNCTION DEFINITION ───────────────────────────────────────────────
    def parse_func_def(self) -> Node:
        node = Node("func_def")
        # return type
        type_tok = self.eat(ttype="KEYWORD")
        node.add(self.leaf(type_tok.lexeme))
        # optional *
        if self.check("*"):
            self.eat(); node.add(self.leaf("*"))
        # function name
        name_tok = self.eat(ttype="IDENTIFIER")
        id_n = Node("id"); id_n.add(self.leaf(name_tok.lexeme))
        node.add(id_n)
        self.eat("("); node.add(self.leaf("("))
        node.add(self.parse_param_list())
        self.eat(")"); node.add(self.leaf(")"))
        node.add(self.parse_compound_stmt())
        return node

    def parse_param_list(self) -> Node:
        node = Node("param_list")
        if self.check(")"):
            node.add(self.leaf("ε")); return node
        if self.check("void") and self.peek(1) and self.peek(1).lexeme == ")":
            self.eat(); node.add(self.leaf("void")); return node
        node.add(self.parse_param())
        while self.match(","):
            node.add(self.leaf(","))
            node.add(self.parse_param())
        return node

    def parse_param(self) -> Node:
        node = Node("param")
        type_tok = self.eat(ttype="KEYWORD")
        node.add(self.leaf(type_tok.lexeme))
        if self.check(ttype="IDENTIFIER"):
            name = self.eat()
            idn = Node("id"); idn.add(self.leaf(name.lexeme)); node.add(idn)
        return node

    # ── COMPOUND STATEMENT { ... } ────────────────────────────────────────
    def parse_compound_stmt(self) -> Node:
        node = Node("compound_stmt")
        self.eat("{"); node.add(self.leaf("{"))
        node.add(self.parse_block_item_list())
        self.eat("}"); node.add(self.leaf("}"))
        return node

    def parse_block_item_list(self) -> Node:
        node = Node("block_item_list")
        while not self.check("}") and not self.at_end():
            node.add(self.parse_block_item())
        if not node.children:
            node.add(self.leaf("ε"))
        return node

    def parse_block_item(self) -> Node:
        node = Node("block_item")
        if self.is_type_kw() and not self._looks_like_func_def():
            node.add(self.parse_local_decl())
        else:
            node.add(self.parse_stmt())
        return node

    # ── LOCAL DECLARATION ─────────────────────────────────────────────────
    def parse_local_decl(self) -> Node:
        node = Node("local_decl")
        type_tok = self.eat(ttype="KEYWORD")
        node.add(self.leaf(type_tok.lexeme))
        node.add(self.parse_declarator_list())
        self.eat(";"); node.add(self.leaf(";"))
        return node

    def parse_declarator_list(self) -> Node:
        node = Node("declarator_list")
        node.add(self.parse_declarator())
        while self.check(","):
            self.eat(","); node.add(self.leaf(","))
            node.add(self.parse_declarator())
        return node

    def parse_declarator(self) -> Node:
        node = Node("declarator")
        name = self.eat(ttype="IDENTIFIER")
        idn = Node("id"); idn.add(self.leaf(name.lexeme)); node.add(idn)
        if self.check("["):
            self.eat("["); node.add(self.leaf("["))
            if not self.check("]"):
                node.add(self.parse_expr())
            self.eat("]"); node.add(self.leaf("]"))
        elif self.check("="):
            self.eat("="); node.add(self.leaf("="))
            node.add(self.parse_assign_expr())
        return node

    # ── STATEMENTS ────────────────────────────────────────────────────────
    def parse_stmt(self) -> Node:
        node = Node("stmt")
        t = self.peek()
        if t is None:
            raise ParseError("Unexpected end of input in statement")

        if t.lexeme == "{":
            node.add(self.parse_compound_stmt()); return node
        if t.lexeme == "if":
            node.add(self.parse_if_stmt()); return node
        if t.lexeme == "while":
            node.add(self.parse_while_stmt()); return node
        if t.lexeme == "for":
            node.add(self.parse_for_stmt()); return node
        if t.lexeme == "do":
            node.add(self.parse_do_while_stmt()); return node
        if t.lexeme == "return":
            node.add(self.parse_return_stmt()); return node
        if t.lexeme == "break":
            node.add(self.parse_break_stmt()); return node
        if t.lexeme == "continue":
            node.add(self.parse_continue_stmt()); return node

        # expression statement (assignment, function call, ++i, etc.)
        node.add(self.parse_expr_stmt())
        return node

    def parse_if_stmt(self) -> Node:
        node = Node("if_stmt")
        self.eat("if");  node.add(self.leaf("if"))
        self.eat("(");   node.add(self.leaf("("))
        node.add(self.parse_expr())
        self.eat(")");   node.add(self.leaf(")"))
        node.add(self.parse_stmt())
        if self.check("else"):
            self.eat("else"); node.add(self.leaf("else"))
            node.add(self.parse_stmt())
        return node

    def parse_while_stmt(self) -> Node:
        node = Node("while_stmt")
        self.eat("while"); node.add(self.leaf("while"))
        self.eat("(");     node.add(self.leaf("("))
        node.add(self.parse_expr())
        self.eat(")");     node.add(self.leaf(")"))
        node.add(self.parse_stmt())
        return node

    def parse_for_stmt(self) -> Node:
        node = Node("for_stmt")
        self.eat("for"); node.add(self.leaf("for"))
        self.eat("(");   node.add(self.leaf("("))
        # init: declaration or expression-stmt (both end with ";")
        if self.is_type_kw():
            node.add(self.parse_local_decl())
        else:
            node.add(self.parse_expr_stmt())
        # condition
        cond_n = Node("for_cond")
        if not self.check(";"):
            cond_n.add(self.parse_expr())
        else:
            cond_n.add(self.leaf("ε"))
        node.add(cond_n)
        self.eat(";"); node.add(self.leaf(";"))
        # increment
        inc_n = Node("for_inc")
        if not self.check(")"):
            inc_n.add(self.parse_expr())
        else:
            inc_n.add(self.leaf("ε"))
        node.add(inc_n)
        self.eat(")"); node.add(self.leaf(")"))
        node.add(self.parse_stmt())
        return node

    def parse_do_while_stmt(self) -> Node:
        node = Node("do_while_stmt")
        self.eat("do");   node.add(self.leaf("do"))
        node.add(self.parse_compound_stmt())
        self.eat("while"); node.add(self.leaf("while"))
        self.eat("(");     node.add(self.leaf("("))
        node.add(self.parse_expr())
        self.eat(")");     node.add(self.leaf(")"))
        self.eat(";");     node.add(self.leaf(";"))
        return node

    def parse_return_stmt(self) -> Node:
        node = Node("return_stmt")
        self.eat("return"); node.add(self.leaf("return"))
        if not self.check(";"):
            node.add(self.parse_expr())
        self.eat(";"); node.add(self.leaf(";"))
        return node

    def parse_break_stmt(self) -> Node:
        node = Node("break_stmt")
        self.eat("break"); node.add(self.leaf("break"))
        self.eat(";"); node.add(self.leaf(";"))
        return node

    def parse_continue_stmt(self) -> Node:
        node = Node("continue_stmt")
        self.eat("continue"); node.add(self.leaf("continue"))
        self.eat(";"); node.add(self.leaf(";"))
        return node

    def parse_expr_stmt(self) -> Node:
        node = Node("expr_stmt")
        if not self.check(";"):
            node.add(self.parse_expr())
        self.eat(";"); node.add(self.leaf(";"))
        return node

    # ── EXPRESSIONS ───────────────────────────────────────────────────────
    def parse_expr(self) -> Node:
        """expr -> assign_expr (',' assign_expr)*"""
        node = self.parse_assign_expr()
        if self.check(","):
            e = Node("expr"); e.add(node)
            while self.check(","):
                self.eat(","); e.add(self.leaf(","))
                e.add(self.parse_assign_expr())
            return e
        return node

    ASSIGN_OPS = {"=", "+=", "-=", "*=", "/="}

    def _is_lvalue_start(self) -> bool:
        t = self.peek()
        return t is not None and t.type == "IDENTIFIER"

    def parse_assign_expr(self) -> Node:
        """assign_expr -> unary_expr assign_op assign_expr | or_expr"""
        saved = self.pos
        # Try lvalue = rvalue
        if self._is_lvalue_start():
            try:
                # optimistically parse a unary_expr (may just be an id)
                left = self.parse_or_expr()
                op_tok = self.peek()
                if op_tok and op_tok.lexeme in self.ASSIGN_OPS:
                    self.eat()
                    node = Node("assign_expr")
                    node.add(left)
                    node.add(self.leaf(op_tok.lexeme))
                    node.add(self.parse_assign_expr())
                    return node
                # not an assignment — return the or_expr we already built
                return left
            except ParseError:
                self.pos = saved
        return self.parse_or_expr()

    def parse_or_expr(self) -> Node:
        node = self.parse_and_expr()
        while self.check("||"):
            op = self.eat()
            right = self.parse_and_expr()
            new = Node("or_expr")
            new.add(node); new.add(self.leaf(op.lexeme)); new.add(right)
            node = new
        return node

    def parse_and_expr(self) -> Node:
        node = self.parse_rel_expr()
        while self.check("&&"):
            op = self.eat()
            right = self.parse_rel_expr()
            new = Node("and_expr")
            new.add(node); new.add(self.leaf(op.lexeme)); new.add(right)
            node = new
        return node

    REL_OPS = {"<", ">", "<=", ">=", "==", "!="}

    def parse_rel_expr(self) -> Node:
        node = self.parse_add_expr()
        while self.peek() and self.peek().lexeme in self.REL_OPS:
            op = self.eat()
            right = self.parse_add_expr()
            new = Node("rel_expr")
            new.add(node); new.add(self.leaf(op.lexeme)); new.add(right)
            node = new
        return node

    def parse_add_expr(self) -> Node:
        node = self.parse_mul_expr()
        while self.peek() and self.peek().lexeme in ("+", "-"):
            # exclude ++ / --
            op = self.eat()
            right = self.parse_mul_expr()
            new = Node("add_expr")
            new.add(node); new.add(self.leaf(op.lexeme)); new.add(right)
            node = new
        return node

    def parse_mul_expr(self) -> Node:
        node = self.parse_unary_expr()
        while self.peek() and self.peek().lexeme in ("*", "/", "%"):
            op = self.eat()
            right = self.parse_unary_expr()
            new = Node("mul_expr")
            new.add(node); new.add(self.leaf(op.lexeme)); new.add(right)
            node = new
        return node

    def parse_unary_expr(self) -> Node:
        t = self.peek()
        if t is None:
            raise ParseError("Expected expression")

        if t.type in ("INC_OP", "DEC_OP"):
            node = Node("unary_expr")
            op = self.eat(); node.add(self.leaf(op.lexeme))
            node.add(self.parse_unary_expr())
            return node

        if t.lexeme in ("!", "-", "+") and t.type in ("NOT_OP", "SUB_OP", "ADD_OP"):
            node = Node("unary_expr")
            op = self.eat(); node.add(self.leaf(op.lexeme))
            node.add(self.parse_unary_expr())
            return node

        if t.lexeme == "sizeof":
            return self.parse_sizeof_expr()

        return self.parse_postfix_expr()

    def parse_postfix_expr(self) -> Node:
        node = self.parse_primary_expr()
        while True:
            t = self.peek()
            if t is None:
                break
            if t.type in ("INC_OP", "DEC_OP"):
                op = self.eat()
                new = Node("postfix_expr")
                new.add(node); new.add(self.leaf(op.lexeme))
                node = new
            elif t.lexeme == "[":
                self.eat("[")
                new = Node("subscript_expr")
                new.add(node); new.add(self.leaf("["))
                new.add(self.parse_expr())
                self.eat("]"); new.add(self.leaf("]"))
                node = new
            elif t.lexeme == "(":
                # function call
                self.eat("(")
                new = Node("call_expr")
                new.add(node); new.add(self.leaf("("))
                new.add(self.parse_arg_list())
                self.eat(")"); new.add(self.leaf(")"))
                node = new
            else:
                break
        return node

    def parse_primary_expr(self) -> Node:
        t = self.peek()
        if t is None:
            raise ParseError("Expected primary expression, got end of input")

        if t.lexeme == "(":
            node = Node("paren_expr")
            self.eat("("); node.add(self.leaf("("))
            node.add(self.parse_expr())
            self.eat(")"); node.add(self.leaf(")"))
            return node

        if t.type == "IDENTIFIER":
            node = Node("id")
            self.eat(); node.add(self.leaf(t.lexeme))
            return node

        if t.type in ("INT_CONST", "FLOAT_CONST", "CONSTANT"):
            node = Node("num")
            self.eat(); node.add(self.leaf(t.lexeme))
            return node

        if t.type == "CHAR_CONST":
            node = Node("char_const")
            self.eat(); node.add(self.leaf(t.lexeme))
            return node

        if t.type == "STRING_LITERAL":
            node = Node("string_lit")
            self.eat(); node.add(self.leaf(t.lexeme))
            return node

        raise ParseError(
            f"Line {t.line}: unexpected token '{t.lexeme}' in expression"
        )

    def parse_sizeof_expr(self) -> Node:
        node = Node("sizeof_expr")
        self.eat("sizeof"); node.add(self.leaf("sizeof"))
        if self.check("("):
            self.eat("("); node.add(self.leaf("("))
            if self.is_type_kw():
                t = self.eat(); node.add(self.leaf(t.lexeme))
            else:
                node.add(self.parse_expr())
            self.eat(")"); node.add(self.leaf(")"))
        else:
            node.add(self.parse_unary_expr())
        return node

    def parse_arg_list(self) -> Node:
        node = Node("arg_list")
        if self.check(")"):
            node.add(self.leaf("ε")); return node
        node.add(self.parse_assign_expr())
        while self.check(","):
            self.eat(","); node.add(self.leaf(","))
            node.add(self.parse_assign_expr())
        return node


# ─────────────────────────────── Public API ──────────────────────────────────
def parse(source: str):
    """
    Returns (tree, tokens, lex_errors, parse_error_str)
    tree is None on parse failure.
    """
    tokens, lex_errors = tokenize(source)
    # filter to only non-hash tokens for parser
    parser_tokens = [t for t in tokens if t.type != "HASH"]
    p = Parser(parser_tokens)
    try:
        tree = p.parse_program()
        return tree, tokens, lex_errors, None
    except ParseError as e:
        return None, tokens, lex_errors, str(e)


# ─────────────────────────────── Text render ─────────────────────────────────
def tree_to_text(root: Node, indent="") -> list[str]:
    lines = []
    def walk(n, prefix="", last=True):
        conn = "└── " if last else "├── "
        lines.append(prefix + conn + n.label)
        new = prefix + ("    " if last else "│   ")
        for i, c in enumerate(n.children):
            walk(c, new, i == len(n.children) - 1)
    walk(root)
    return lines


if __name__ == "__main__":
    import sys
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else \
        "int main() { int a = 10; return 0; }"
    tree, toks, lerrs, perr = parse(src)
    if perr:
        print("PARSE ERROR:", perr)
    else:
        for line in tree_to_text(tree):
            print(line)
