"""
Mini C Compiler — Phase 1 (Lexical Analysis) + Phase 2 (Syntax Analysis)
=========================================================================
Tkinter GUI — no external database required.

Features
--------
• Full C-subset lexer (handles all 21 sample programs)
• Robust recursive-descent parser with correct parse tree for every program
• Token table with colour-coded rows
• Interactive text parse tree
• Graphical parse tree via canvas (with zoom + scroll)
• 21 built-in sample programs, selectable from a list
• Symbol table
• Error display with line numbers
• Export parse tree as text file

Run:
    python tk_app.py
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import math

from lexer import tokenize, PATTERNS
from parser import parse, tree_to_text, Node

# ─────────────────────────── Sample Programs ─────────────────────────────────
SAMPLES = {
    "Prog 1 — Rectangle border (*) [for/nested]": """\
#include <stdio.h>
int main() {
    int i, j, n = 5;
    for(i = 1; i <= n; i++) {
        for(j = 1; j <= n; j++) {
            if(i == 1 || i == n || j == 1 || j == n)
                printf("* ");
            else
                printf("  ");
        }
        printf("\\n");
    }
    return 0;
}""",

    "Prog 2 — Multiplication table [nested for]": """\
#include <stdio.h>
int main() {
    int i, j;
    for(i = 1; i <= 5; i++) {
        for(j = 1; j <= 5; j++) {
            printf("%d ", i * j);
        }
        printf("\\n");
    }
    return 0;
}""",

    "Prog 3 — Number pattern [nested for]": """\
#include <stdio.h>
int main() {
    int i, j;
    for(i = 1; i <= 5; i++) {
        for(j = 1; j <= i; j++) {
            printf("%d ", j);
        }
        printf("\\n");
    }
    printf("Pattern complete\\n");
    return 0;
}""",

    "Prog 4 — Chessboard pattern [for/if modulo]": """\
#include <stdio.h>
int main()
{
    int i, j;
    for(i = 1; i <= 8; i++) {
        for(j = 1; j <= 8; j++) {
            if((i + j) % 2 == 0)
                printf("W ");
            else
                printf("B ");
        }
        printf("\\n");
    }
    return 0;
}""",

    "Prog 5 — Star triangle [nested for]": """\
#include <stdio.h>
int main()
{
    int i, j;
    for(i = 1; i <= 5; i++) {
        for(j = 1; j <= i; j++) {
            printf("* ");
        }
        printf("\\n");
    }
    return 0;
}""",

    "Prog 6 — Pascal's triangle [for + coef]": """\
#include <stdio.h>
int main() {
    int i, j, n = 6, coef;
    for(i = 0; i < n; i++) {
        for(j = 1; j < n - i; j++)
            printf(" ");
        coef = 1;
        for(j = 0; j <= i; j++) {
            printf("%d ", coef);
            coef = coef * (i - j) / (j + 1);
        }
        printf("\\n");
    }
    return 0;
}""",

    "Prog 7 — Star pyramid [nested for]": """\
#include <stdio.h>
int main() {
    int i, j, n = 5;
    for(i = 1; i <= n; i++) {
        for(j = 1; j <= n - i; j++)
            printf(" ");
        for(j = 1; j <= 2 * i - 1; j++)
            printf("*");
        printf("\\n");
    }
    return 0;
}""",

    "Prog 8 — Palindrome check [while]": """\
#include <stdio.h>
int main() {
    int num = 121, temp, rev = 0, digit;
    temp = num;
    while(num != 0) {
        digit = num % 10;
        rev = rev * 10 + digit;
        num = num / 10;
    }
    if(temp == rev)
        printf("Palindrome\\n");
    else
        printf("Not Palindrome\\n");
    return 0;
}""",

    "Prog 9 — While loop counter": """\
#include <stdio.h>
int main() {
    int i = 1;
    while(i <= 5) {
        printf("Value: %d\\n", i);
        i++;
    }
    printf("Loop ended\\n");
    return 0;
}""",

    "Prog 10 — Sum of digits [while]": """\
#include <stdio.h>
int main() {
    int num = 1234, sum = 0, digit;
    while(num != 0) {
        digit = num % 10;
        sum = sum + digit;
        num = num / 10;
    }
    printf("Sum of digits = %d\\n", sum);
    return 0;
}""",

    "Prog 11 — Reverse number [while + /=]": """\
#include <stdio.h>
int main()
{
    int num = 1234, rev = 0, rem;
    while(num != 0) {
        rem = num % 10;
        rev = rev * 10 + rem;
        num /= 10;
    }
    printf("Reverse = %d", rev);
    return 0;
}""",

    "Prog 12 — While loop (Number:)": """\
#include <stdio.h>
int main()
{
    int i = 1;
    while(i <= 5) {
        printf("Number: %d\\n", i);
        i++;
    }
    printf("Loop Ended");
    return 0;
}""",

    "Prog 13 — Char classify [if/else-if chain]": """\
#include <stdio.h>
int main() {
    char ch = 'A';
    if((ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z')) {
        if(ch == 'a' || ch == 'e' || ch == 'i' || ch == 'o' || ch == 'u' ||
           ch == 'A' || ch == 'E' || ch == 'I' || ch == 'O' || ch == 'U')
            printf("Vowel\\n");
        else
            printf("Consonant\\n");
    } else if(ch >= '0' && ch <= '9') {
        printf("Digit\\n");
    } else {
        printf("Special Character\\n");
    }
    return 0;
}""",

    "Prog 14 — Largest of 3 [if/else-if]": """\
#include <stdio.h>
int main() {
    int a = 10, b = 25, c = 15;
    if(a > b && a > c) {
        printf("Largest is a = %d\\n", a);
    } else if(b > c) {
        printf("Largest is b = %d\\n", b);
    } else {
        printf("Largest is c = %d\\n", c);
    }
    return 0;
}""",

    "Prog 15 — Grade system [if/else-if]": """\
#include <stdio.h>
int main()
{
    int marks = 75;
    if(marks >= 90)
        printf("Grade A");
    else if(marks >= 75)
        printf("Grade B");
    else if(marks >= 50)
        printf("Grade C");
    else
        printf("Fail");
    return 0;
}""",

    "Prog 16 — Income tax [if/else-if]": """\
#include <stdio.h>
int main() {
    float income = 600000, tax;
    if(income <= 250000)
        tax = 0;
    else if(income <= 500000)
        tax = income * 0.05;
    else if(income <= 1000000)
        tax = income * 0.2;
    else
        tax = income * 0.3;
    printf("Tax = %.2f", tax);
    return 0;
}""",

    "Prog 17 — Leap year [nested if]": """\
#include <stdio.h>
int main() {
    int year = 2024;
    if(year % 4 == 0) {
        if(year % 100 == 0) {
            if(year % 400 == 0)
                printf("Leap Year\\n");
            else
                printf("Not Leap Year\\n");
        } else {
            printf("Leap Year\\n");
        }
    } else {
        printf("Not Leap Year\\n");
    }
    return 0;
}""",

    "Prog 18 — Positive/Negative Even/Odd [nested if]": """\
#include <stdio.h>
int main() {
    int num = -4;
    if(num > 0) {
        if(num % 2 == 0)
            printf("Positive Even\\n");
        else
            printf("Positive Odd\\n");
    } else if(num < 0) {
        if(num % 2 == 0)
            printf("Negative Even\\n");
        else
            printf("Negative Odd\\n");
    } else {
        printf("Number is Zero\\n");
    }
    return 0;
}""",

    "Prog 19 — Two positives check [nested if]": """\
#include <stdio.h>
int main() {
    int a = 10, b = 20;
    if(a > 0) {
        if(b > 0) {
            printf("Both numbers are positive\\n");
        } else {
            printf("a is positive, b is not\\n");
        }
    } else {
        printf("a is not positive\\n");
    }
    return 0;
}""",

    "Prog 20 — Positive/Negative [nested if v2]": """\
#include <stdio.h>
int main()
{
    int a = 10, b = 20;
    if(a > 0) {
        if(b > 0)
            printf("Both are positive");
        else
            printf("a positive, b negative");
    } else {
        printf("a is negative");
    }
    return 0;
}""",

    "Prog 21 — Login access control [nested if]": """\
#include <stdio.h>
int main()
{
    int input = 1234, password = 1234, time = 20;
    if(input == password) {
        if(time < 21) {
            printf("Access Granted\\n");
        } else {
            printf("Late Night - Access Limited\\n");
        }
    } else {
        printf("Wrong Password\\n");
    }
    return 0;
}""",

    "Custom Expression": "k = x + y - z * w;",
}

# ──────────────────────────── Token colours ──────────────────────────────────
TOKEN_COLORS = {
    "KEYWORD":        ("#1a3a6e", "#dce8ff"),
    "IDENTIFIER":     ("#1a4a1a", "#dcf0dc"),
    "INT_CONST":      ("#5a2a00", "#ffeedd"),
    "FLOAT_CONST":    ("#5a2a00", "#ffeedd"),
    "CONSTANT":       ("#5a2a00", "#ffeedd"),
    "STRING_LITERAL": ("#6a0050", "#ffeeff"),
    "CHAR_CONST":     ("#6a0050", "#ffeeff"),
    "ASSIGN_OP":      ("#444400", "#fffff0"),
    "ADD_OP":         ("#003344", "#e0f8ff"),
    "SUB_OP":         ("#003344", "#e0f8ff"),
    "MUL_OP":         ("#003344", "#e0f8ff"),
    "DIV_OP":         ("#003344", "#e0f8ff"),
    "MOD_OP":         ("#003344", "#e0f8ff"),
    "INC_OP":         ("#003344", "#e0f8ff"),
    "DEC_OP":         ("#003344", "#e0f8ff"),
    "REL_OP":         ("#4a0000", "#ffe8e8"),
    "LOGICAL_OP":     ("#3a0060", "#f0e8ff"),
    "NOT_OP":         ("#3a0060", "#f0e8ff"),
    "BRACKET":        ("#303030", "#f4f4f4"),
    "SPECIAL_CHAR":   ("#303030", "#f4f4f4"),
    "HASH":           ("#555500", "#fffff0"),
    "UNKNOWN":        ("#aa0000", "#ffe0e0"),
}


# ─────────────────────────────── Canvas Tree ─────────────────────────────────
class TreeCanvas(tk.Canvas):
    """
    Draws a parse tree on a scrollable canvas using a Reingold-Tilford-
    inspired layout (simple recursive approach).
    """
    NODE_W = 80
    NODE_H = 30
    H_GAP  = 10
    V_GAP  = 40

    def __init__(self, master, **kw):
        super().__init__(master, bg="#f8f8f8", **kw)
        self._scale = 1.0
        self._positions: dict = {}

    def draw(self, root: Node):
        self.delete("all")
        if root is None:
            self.create_text(200, 80, text="No parse tree.",
                             font=("Helvetica", 14), fill="#999")
            return
        # layout
        pos = {}
        self._layout(root, pos, 0, [0])
        # shift so min_x = 20
        if pos:
            min_x = min(x for x, y in pos.values())
            pos = {id(n): (x - min_x + 60, y) for n, (x, y) in
                   {n: pos[id(n)] for n in self._all_nodes(root)}.items()}

        # find max coords for scroll region
        if pos:
            max_x = max(x for x, y in pos.values()) + self.NODE_W + 20
            max_y = max(y for x, y in pos.values()) + self.NODE_H + 20
            self.configure(scrollregion=(0, 0, max_x, max_y))

        self._draw_recursive(root, pos)

    def _all_nodes(self, n):
        yield n
        for c in n.children:
            yield from self._all_nodes(c)

    def _layout(self, node, pos, depth, x_counter):
        """Simple left-to-right placement; returns x centre."""
        y = 20 + depth * (self.NODE_H + self.V_GAP)
        if not node.children:
            x = x_counter[0] * (self.NODE_W + self.H_GAP) + 20
            x_counter[0] += 1
            pos[id(node)] = (x, y)
            return x + self.NODE_W // 2

        child_xs = []
        for c in node.children:
            cx = self._layout(c, pos, depth + 1, x_counter)
            child_xs.append(cx)
        x_centre = (child_xs[0] + child_xs[-1]) / 2
        x = int(x_centre - self.NODE_W / 2)
        pos[id(node)] = (x, y)
        return x_centre

    def _draw_recursive(self, node, pos):
        x, y = pos[id(node)]
        cx = x + self.NODE_W // 2
        cy = y + self.NODE_H // 2

        # draw edges to children first (behind nodes)
        for child in node.children:
            cx2, cy2_top = pos[id(child)][0] + self.NODE_W // 2, pos[id(child)][1]
            self.create_line(cx, y + self.NODE_H, cx2, cy2_top,
                             fill="#888", width=1)

        # node box
        is_leaf = not node.children
        fill   = "#FAEEDA" if is_leaf else "#E6F1FB"
        outline = "#854F0B" if is_leaf else "#185FA5"
        self.create_rectangle(x, y, x + self.NODE_W, y + self.NODE_H,
                               fill=fill, outline=outline, width=1)
        label = node.label
        if len(label) > 10:
            label = label[:9] + "…"
        self.create_text(cx, cy, text=label, font=("Helvetica", 8),
                         fill=outline)

        for child in node.children:
            self._draw_recursive(child, pos)


# ─────────────────────────────── Main GUI ────────────────────────────────────
class CompilerApp:
    def __init__(self, root: tk.Tk):
        root.title("Mini C Compiler — Phase 1 (Lexer) + Phase 2 (Parser)")
        root.geometry("1280x820")
        root.configure(bg="#2b2b2b")

        self._build_ui(root)

        # load first sample
        first = next(iter(SAMPLES))
        self.sample_var.set(first)
        self._load_sample()

    # ── UI construction ───────────────────────────────────────────────────
    def _build_ui(self, root):
        # ── top bar ──────────────────────────────────────────────────────
        top = tk.Frame(root, bg="#1e1e1e", pady=6)
        top.pack(fill="x")

        tk.Label(top, text="⚙ Mini C Compiler",
                 font=("Helvetica", 15, "bold"),
                 fg="white", bg="#1e1e1e").pack(side="left", padx=14)

        tk.Label(top, text="Sample:", fg="#aaa", bg="#1e1e1e",
                 font=("Helvetica", 10)).pack(side="left", padx=(20, 4))
        self.sample_var = tk.StringVar()
        cbo = ttk.Combobox(top, textvariable=self.sample_var,
                            values=list(SAMPLES.keys()), width=42,
                            state="readonly")
        cbo.pack(side="left")
        cbo.bind("<<ComboboxSelected>>", lambda _: self._load_sample())

        btn_style = {"bg": "#0a84ff", "fg": "white",
                     "font": ("Helvetica", 10, "bold"),
                     "relief": "flat", "padx": 12, "pady": 4,
                     "cursor": "hand2"}
        tk.Button(top, text="▶  Compile",
                  command=self._compile, **btn_style).pack(side="left", padx=14)
        tk.Button(top, text="💾  Export tree",
                  command=self._export_tree,
                  bg="#30a050", fg="white",
                  font=("Helvetica", 10, "bold"),
                  relief="flat", padx=10, pady=4,
                  cursor="hand2").pack(side="left")
        tk.Button(top, text="🗑  Clear",
                  command=self._clear,
                  bg="#888", fg="white",
                  font=("Helvetica", 10, "bold"),
                  relief="flat", padx=10, pady=4,
                  cursor="hand2").pack(side="left", padx=10)

        # ── paned: left=editor, right=results ────────────────────────────
        paned = tk.PanedWindow(root, orient="horizontal",
                                sashwidth=6, bg="#444")
        paned.pack(fill="both", expand=True, padx=6, pady=6)

        # ── LEFT: editor + status ─────────────────────────────────────────
        left = tk.Frame(paned, bg="#2b2b2b")
        paned.add(left, minsize=360)

        tk.Label(left, text="Source Code (C)",
                 font=("Helvetica", 11, "bold"),
                 fg="#ccc", bg="#2b2b2b").pack(anchor="w", padx=6, pady=(4, 0))
        self.editor = scrolledtext.ScrolledText(
            left, font=("Courier New", 11),
            bg="#1e1e1e", fg="#dcdcdc",
            insertbackground="white",
            relief="flat", wrap="none")
        self.editor.pack(fill="both", expand=True, padx=6, pady=4)

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(left, textvariable=self.status_var,
                 font=("Courier New", 9), fg="#8f8",
                 bg="#1e1e1e", anchor="w", relief="sunken").pack(
            fill="x", padx=6, pady=(0, 4))

        # ── RIGHT: notebook ───────────────────────────────────────────────
        right = tk.Frame(paned, bg="#2b2b2b")
        paned.add(right, minsize=600)

        nb = ttk.Notebook(right)
        nb.pack(fill="both", expand=True)

        # TAB 1: Tokens
        f1 = ttk.Frame(nb); nb.add(f1, text="  Phase 1 — Tokens  ")
        self._build_token_tab(f1)

        # TAB 2: Symbol Table
        f2 = ttk.Frame(nb); nb.add(f2, text="  Symbol Table  ")
        self._build_symbol_tab(f2)

        # TAB 3: Parse Tree (text)
        f3 = ttk.Frame(nb); nb.add(f3, text="  Phase 2 — Parse Tree (text)  ")
        self.tree_text = scrolledtext.ScrolledText(
            f3, font=("Courier New", 10), wrap="none",
            bg="#1c1c2e", fg="#e0e0ff", relief="flat")
        self.tree_text.pack(fill="both", expand=True, padx=4, pady=4)

        # TAB 4: Parse Tree (graph)
        f4 = ttk.Frame(nb); nb.add(f4, text="  Parse Tree (visual)  ")
        self._build_canvas_tab(f4)

        # TAB 5: Grammar
        f5 = ttk.Frame(nb); nb.add(f5, text="  Grammar  ")
        self._build_grammar_tab(f5)

    def _build_token_tab(self, parent):
        cols = ("no", "line", "lexeme", "token", "pattern")
        tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col, w in zip(cols, (45, 50, 140, 140, 400)):
            tree.heading(col, text=col.upper())
            tree.column(col, width=w, anchor="w")
        sb_y = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        sb_x = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)
        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")
        tree.pack(fill="both", expand=True)
        self.tok_tree = tree

        # configure tag colours
        for ttype, (fg, bg) in TOKEN_COLORS.items():
            tree.tag_configure(ttype, foreground=fg, background=bg)

    def _build_symbol_tab(self, parent):
        cols = ("symbol", "type", "first_line")
        tree = ttk.Treeview(parent, columns=cols, show="headings")
        for col, w in zip(cols, (160, 140, 80)):
            tree.heading(col, text=col.replace("_", " ").upper())
            tree.column(col, width=w, anchor="w")
        sb = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)
        self.sym_tree = tree

    def _build_canvas_tab(self, parent):
        ctrl = tk.Frame(parent, bg="#f0f0f0")
        ctrl.pack(fill="x")
        tk.Label(ctrl, text="Zoom:", bg="#f0f0f0").pack(side="left", padx=6)
        tk.Button(ctrl, text="+", command=lambda: self._zoom(1.2),
                  width=3).pack(side="left")
        tk.Button(ctrl, text="−", command=lambda: self._zoom(0.8),
                  width=3).pack(side="left")
        tk.Button(ctrl, text="Reset", command=self._zoom_reset,
                  width=6).pack(side="left", padx=4)
        tk.Label(ctrl, text="Scroll to navigate the tree →",
                 fg="#666", bg="#f0f0f0",
                 font=("Helvetica", 9)).pack(side="left", padx=10)

        frame = tk.Frame(parent)
        frame.pack(fill="both", expand=True)
        self.canvas = TreeCanvas(frame)
        hs = ttk.Scrollbar(frame, orient="horizontal",
                            command=self.canvas.xview)
        vs = ttk.Scrollbar(frame, orient="vertical",
                            command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=hs.set, yscrollcommand=vs.set)
        hs.pack(side="bottom", fill="x")
        vs.pack(side="right", fill="y")
        self.canvas.pack(fill="both", expand=True)

    def _build_grammar_tab(self, parent):
        txt = scrolledtext.ScrolledText(parent,
                                         font=("Courier New", 10),
                                         bg="#1c1c2e", fg="#c8d8ff",
                                         wrap="none", relief="flat")
        txt.insert("end", GRAMMAR_TEXT)
        txt.configure(state="disabled")
        txt.pack(fill="both", expand=True, padx=4, pady=4)

    # ── actions ──────────────────────────────────────────────────────────
    def _load_sample(self):
        name = self.sample_var.get()
        src = SAMPLES.get(name, "")
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", src)

    def _clear(self):
        self.editor.delete("1.0", "end")
        for r in self.tok_tree.get_children(): self.tok_tree.delete(r)
        for r in self.sym_tree.get_children(): self.sym_tree.delete(r)
        self.tree_text.delete("1.0", "end")
        self.canvas.delete("all")
        self.status_var.set("Cleared.")

    def _compile(self):
        src = self.editor.get("1.0", "end").rstrip()
        if not src:
            messagebox.showwarning("Empty", "Enter some source code first.")
            return

        # ── Phase 1: Lex ────────────────────────────────────────────────
        tokens, lex_errors = tokenize(src)

        # clear old results
        for r in self.tok_tree.get_children(): self.tok_tree.delete(r)
        for r in self.sym_tree.get_children(): self.sym_tree.delete(r)

        # populate token table
        for i, t in enumerate(tokens, 1):
            tag = t.type if t.type in TOKEN_COLORS else "UNKNOWN"
            self.tok_tree.insert("", "end",
                                  values=(i, t.line, t.lexeme, t.type, t.pattern),
                                  tags=(tag,))

        # symbol table
        seen, rows = set(), []
        for t in tokens:
            if t.type in ("IDENTIFIER", "INT_CONST", "FLOAT_CONST",
                          "CONSTANT", "CHAR_CONST") and t.lexeme not in seen:
                seen.add(t.lexeme)
                rows.append((t.lexeme, t.type, t.line))
        for sym, typ, ln in rows:
            self.sym_tree.insert("", "end", values=(sym, typ, ln))

        # ── Phase 2: Parse ──────────────────────────────────────────────
        tree, _, _, parse_err = parse(src)

        # text tree
        self.tree_text.delete("1.0", "end")
        if parse_err:
            self.tree_text.insert("end", f"❌ Syntax Error:\n{parse_err}\n")
            self.canvas.delete("all")
            self.canvas.create_text(200, 80, text=f"Parse Error:\n{parse_err}",
                                     font=("Helvetica", 12), fill="#c00")
        elif tree is not None:
            lines = tree_to_text(tree)
            self.tree_text.insert("end", "\n".join(lines))
            self.canvas.draw(tree)
        else:
            self.tree_text.insert("end", "(empty program)")
            self.canvas.delete("all")

        # status bar
        lex_status = "OK" if not lex_errors else f"{len(lex_errors)} error(s)"
        par_status = "OK" if not parse_err else "FAILED"
        msg = (f"Tokens: {len(tokens)}   │   "
               f"Lex: {lex_status}   │   Parser: {par_status}")
        self.status_var.set(msg)

        if lex_errors:
            messagebox.showwarning("Lexical Errors",
                                   "\n".join(lex_errors[:10]))

        if parse_err:
            messagebox.showerror("Parse Error", parse_err)

        # remember tree for export
        self._last_tree = tree

    def _export_tree(self):
        tree = getattr(self, "_last_tree", None)
        if tree is None:
            messagebox.showinfo("No tree", "Compile a program first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Export parse tree")
        if not path:
            return
        lines = tree_to_text(tree)
        with open(path, "w") as f:
            f.write("\n".join(lines))
        messagebox.showinfo("Exported", f"Tree saved to:\n{path}")

    def _zoom(self, factor):
        self.canvas.scale("all",
                          self.canvas.winfo_width() / 2,
                          self.canvas.winfo_height() / 2,
                          factor, factor)

    def _zoom_reset(self):
        tree = getattr(self, "_last_tree", None)
        if tree:
            self.canvas.draw(tree)


# ──────────────────────────── Grammar text ───────────────────────────────────
GRAMMAR_TEXT = """\
Mini C Grammar (used by the recursive-descent parser)
======================================================

program          -> include_list  translation_unit

include_list     -> ('#' 'include' HEADER)*  |  ε

translation_unit -> (func_def | global_decl)*

func_def         -> type  id  '(' param_list ')'  compound_stmt

param_list       -> ε  |  'void'  |  param (',' param)*
param            -> type  id

compound_stmt    -> '{'  block_item_list  '}'

block_item_list  -> block_item*  |  ε
block_item       -> local_decl  |  stmt

local_decl       -> type  declarator_list  ';'
declarator_list  -> declarator (',' declarator)*
declarator       -> id  ('=' assign_expr)?
                  | id  '[' expr ']'

stmt             -> expr_stmt
                  | compound_stmt
                  | if_stmt
                  | while_stmt
                  | for_stmt
                  | do_while_stmt
                  | return_stmt
                  | break_stmt
                  | continue_stmt

if_stmt          -> 'if' '(' expr ')' stmt ('else' stmt)?
while_stmt       -> 'while' '(' expr ')' stmt
for_stmt         -> 'for' '(' (local_decl | expr_stmt)  expr? ';'  expr? ')' stmt
do_while_stmt    -> 'do' compound_stmt 'while' '(' expr ')' ';'
return_stmt      -> 'return' expr? ';'
break_stmt       -> 'break' ';'
continue_stmt    -> 'continue' ';'
expr_stmt        -> expr? ';'

expr             -> assign_expr (',' assign_expr)*
assign_expr      -> or_expr (assign_op assign_expr)?
assign_op        -> '=' | '+=' | '-=' | '*=' | '/='
or_expr          -> and_expr ('||' and_expr)*
and_expr         -> rel_expr ('&&' rel_expr)*
rel_expr         -> add_expr (('<'|'>'|'<='|'>='|'=='|'!=') add_expr)*
add_expr         -> mul_expr (('+' | '-') mul_expr)*
mul_expr         -> unary_expr (('*' | '/' | '%') unary_expr)*
unary_expr       -> ('!' | '-' | '++' | '--') unary_expr
                  | postfix_expr
postfix_expr     -> primary_expr ('++'|'--'|'['expr']'|'('arg_list')')*
primary_expr     -> id
                  | INT_CONST | FLOAT_CONST | CHAR_CONST
                  | STRING_LITERAL
                  | '(' expr ')'
arg_list         -> ε  |  assign_expr (',' assign_expr)*
"""


# ─────────────────────────────── Entry ───────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    try:
        from tkinter import font as tkfont
        default = tkfont.nametofont("TkDefaultFont")
        default.configure(size=10)
    except Exception:
        pass

    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    CompilerApp(root)
    root.mainloop()
