"""
Phase 1: Lexical Analyzer
--------------------------
DFA-style scanner for a broad C subset.
Handles: keywords, identifiers, integer/float constants, string & char
literals, all operators (including ++, --, +=, -=, etc.),
preprocessor directives, line/block comments, and brackets.
"""

# Human-readable patterns shown in the token table
PATTERNS = {
    "KEYWORD":        "int|float|char|double|void|if|else|while|for|do|"
                      "return|break|continue|struct|typedef|sizeof|include|"
                      "main|printf|scanf",
    "IDENTIFIER":     "[a-zA-Z_][a-zA-Z0-9_]*",
    "INT_CONST":      "[0-9]+",
    "FLOAT_CONST":    "[0-9]+\\.[0-9]+",
    "CHAR_CONST":     "'[^'\\\\]'",
    "STRING_LITERAL": '"[^"]*"',
    "ASSIGN_OP":      "= | += | -= | *= | /=",
    "ADD_OP":         "+",
    "SUB_OP":         "-",
    "MUL_OP":         "*",
    "DIV_OP":         "/",
    "MOD_OP":         "%",
    "INC_OP":         "++",
    "DEC_OP":         "--",
    "REL_OP":         "< | > | <= | >= | == | !=",
    "LOGICAL_OP":     "&& | ||",
    "NOT_OP":         "!",
    "BRACKET":        "( | ) | { | } | [ | ]",
    "SPECIAL_CHAR":   "; | , | .",
    "HASH":           "#",
    "UNKNOWN":        "any other character",
}

KEYWORDS = {
    "int", "float", "char", "double", "void",
    "if", "else", "while", "for", "do",
    "return", "break", "continue",
    "struct", "typedef", "sizeof",
}

# identifiers that behave like keywords in context
STDLIB_FUNCS = {"printf", "scanf", "main"}


class Token:
    def __init__(self, lexeme, token_type, pattern, line):
        self.lexeme = lexeme
        self.type = token_type
        self.pattern = pattern
        self.line = line

    def __repr__(self):
        return f"<{self.type}, '{self.lexeme}', line {self.line}>"


def tokenize(source: str):
    tokens, errors = [], []
    i, line, n = 0, 1, len(source)

    def peek(offset=0):
        idx = i + offset
        return source[idx] if idx < n else ""

    while i < n:
        ch = source[i]

        # ── whitespace ──────────────────────────────────────────────────
        if ch == "\n":
            line += 1; i += 1; continue
        if ch in " \t\r":
            i += 1; continue

        # ── // line comment ─────────────────────────────────────────────
        if ch == "/" and peek(1) == "/":
            while i < n and source[i] != "\n":
                i += 1
            continue

        # ── /* block comment */ ─────────────────────────────────────────
        if ch == "/" and peek(1) == "*":
            i += 2
            while i + 1 < n and not (source[i] == "*" and source[i+1] == "/"):
                if source[i] == "\n": line += 1
                i += 1
            i += 2; continue

        # ── # preprocessor — skip whole line ───────────────────────────
        if ch == "#":
            tokens.append(Token(ch, "HASH", PATTERNS["HASH"], line))
            i += 1
            # collect rest of line as identifier tokens (e.g. include, <stdio.h>)
            while i < n and source[i] != "\n":
                c2 = source[i]
                if c2 in " \t":
                    i += 1
                elif c2.isalpha() or c2 == "_":
                    j = i
                    while j < n and (source[j].isalnum() or source[j] == "_"):
                        j += 1
                    lex = source[i:j]
                    tt = "KEYWORD" if lex in ("include", "define") else "IDENTIFIER"
                    tokens.append(Token(lex, tt, PATTERNS["IDENTIFIER"], line))
                    i = j
                elif c2 == "<":
                    j = i + 1
                    while j < n and source[j] != ">": j += 1
                    tokens.append(Token(source[i:j+1], "STRING_LITERAL",
                                        PATTERNS["STRING_LITERAL"], line))
                    i = j + 1
                elif c2 == '"':
                    j = i + 1
                    while j < n and source[j] != '"': j += 1
                    tokens.append(Token(source[i:j+1], "STRING_LITERAL",
                                        PATTERNS["STRING_LITERAL"], line))
                    i = j + 1
                else:
                    i += 1
            continue

        # ── identifier / keyword ────────────────────────────────────────
        if ch.isalpha() or ch == "_":
            j = i
            while j < n and (source[j].isalnum() or source[j] == "_"):
                j += 1
            lex = source[i:j]
            if lex in KEYWORDS:
                tt, pat = "KEYWORD", PATTERNS["KEYWORD"]
            else:
                tt, pat = "IDENTIFIER", PATTERNS["IDENTIFIER"]
            tokens.append(Token(lex, tt, pat, line))
            i = j; continue

        # ── numeric constant ────────────────────────────────────────────
        if ch.isdigit():
            j = i; dot = False
            while j < n and (source[j].isdigit() or (source[j] == "." and not dot)):
                if source[j] == ".": dot = True
                j += 1
            lex = source[i:j]
            tt = "FLOAT_CONST" if dot else "INT_CONST"
            tokens.append(Token(lex, tt, PATTERNS[tt], line))
            i = j; continue

        # ── char literal ────────────────────────────────────────────────
        if ch == "'":
            j = i + 1
            if j < n and source[j] == "\\":
                j += 2   # escape char
            elif j < n:
                j += 1
            if j < n and source[j] == "'":
                j += 1
            tokens.append(Token(source[i:j], "CHAR_CONST",
                                 PATTERNS["CHAR_CONST"], line))
            i = j; continue

        # ── string literal ──────────────────────────────────────────────
        if ch == '"':
            j = i + 1
            while j < n and source[j] != '"':
                if source[j] == "\\": j += 1   # skip escaped char
                if j < n and source[j] == "\n": line += 1
                j += 1
            if j >= n:
                errors.append(f"Line {line}: unterminated string literal")
                break
            tokens.append(Token(source[i:j+1], "STRING_LITERAL",
                                 PATTERNS["STRING_LITERAL"], line))
            i = j + 1; continue

        # ── two-char operators ──────────────────────────────────────────
        two = source[i:i+2]
        TWO_CHAR = {
            "==": ("REL_OP",    PATTERNS["REL_OP"]),
            "!=": ("REL_OP",    PATTERNS["REL_OP"]),
            "<=": ("REL_OP",    PATTERNS["REL_OP"]),
            ">=": ("REL_OP",    PATTERNS["REL_OP"]),
            "&&": ("LOGICAL_OP",PATTERNS["LOGICAL_OP"]),
            "||": ("LOGICAL_OP",PATTERNS["LOGICAL_OP"]),
            "++": ("INC_OP",   PATTERNS["INC_OP"]),
            "--": ("DEC_OP",   PATTERNS["DEC_OP"]),
            "+=": ("ASSIGN_OP",PATTERNS["ASSIGN_OP"]),
            "-=": ("ASSIGN_OP",PATTERNS["ASSIGN_OP"]),
            "*=": ("ASSIGN_OP",PATTERNS["ASSIGN_OP"]),
            "/=": ("ASSIGN_OP",PATTERNS["ASSIGN_OP"]),
        }
        if two in TWO_CHAR:
            tt, pat = TWO_CHAR[two]
            tokens.append(Token(two, tt, pat, line))
            i += 2; continue

        # ── single-char operators / punctuation ─────────────────────────
        SINGLE = {
            "=": ("ASSIGN_OP",   PATTERNS["ASSIGN_OP"]),
            "+": ("ADD_OP",      PATTERNS["ADD_OP"]),
            "-": ("SUB_OP",      PATTERNS["SUB_OP"]),
            "*": ("MUL_OP",      PATTERNS["MUL_OP"]),
            "/": ("DIV_OP",      PATTERNS["DIV_OP"]),
            "%": ("MOD_OP",      PATTERNS["MOD_OP"]),
            "<": ("REL_OP",      PATTERNS["REL_OP"]),
            ">": ("REL_OP",      PATTERNS["REL_OP"]),
            "!": ("NOT_OP",      PATTERNS["NOT_OP"]),
            "(": ("BRACKET",     PATTERNS["BRACKET"]),
            ")": ("BRACKET",     PATTERNS["BRACKET"]),
            "{": ("BRACKET",     PATTERNS["BRACKET"]),
            "}": ("BRACKET",     PATTERNS["BRACKET"]),
            "[": ("BRACKET",     PATTERNS["BRACKET"]),
            "]": ("BRACKET",     PATTERNS["BRACKET"]),
            ";": ("SPECIAL_CHAR",PATTERNS["SPECIAL_CHAR"]),
            ",": ("SPECIAL_CHAR",PATTERNS["SPECIAL_CHAR"]),
            ".": ("SPECIAL_CHAR",PATTERNS["SPECIAL_CHAR"]),
        }
        if ch in SINGLE:
            tt, pat = SINGLE[ch]
            tokens.append(Token(ch, tt, pat, line))
            i += 1; continue

        errors.append(f"Line {line}: illegal character '{ch}'")
        tokens.append(Token(ch, "UNKNOWN", PATTERNS["UNKNOWN"], line))
        i += 1

    return tokens, errors


if __name__ == "__main__":
    import sys
    src = open(sys.argv[1]).read() if len(sys.argv) > 1 else "int a = 10 + 5;"
    toks, errs = tokenize(src)
    print(f"{'#':<4}{'LINE':<6}{'LEXEME':<18}{'TOKEN':<16}PATTERN")
    print("-" * 90)
    for idx, t in enumerate(toks, 1):
        print(f"{idx:<4}{t.line:<6}{t.lexeme:<18}{t.type:<16}{t.pattern}")
    if errs:
        print("\nLexical errors:")
        for e in errs: print(" ", e)
