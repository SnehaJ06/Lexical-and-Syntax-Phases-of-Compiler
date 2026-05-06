"""
cli_test.py — Command-line test / demo for the Mini C Compiler
==============================================================
Run without arguments to test all 21 built-in sample programs.
Run with a file path to compile a .c file from disk.

Usage:
    python cli_test.py                   # test all 21 programs
    python cli_test.py myfile.c          # compile a specific file
    python cli_test.py --tree myfile.c   # show full parse tree
"""

import sys
import os

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import tokenize
from parser import parse, tree_to_text

SAMPLES = {
    "Prog 1 — Rectangle border (for/nested)": """\
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

    "Prog 2 — Multiplication table": """\
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

    "Prog 3 — Number pattern": """\
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

    "Prog 4 — Chessboard pattern": """\
#include <stdio.h>
int main() {
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

    "Prog 5 — Star triangle": """\
#include <stdio.h>
int main() {
    int i, j;
    for(i = 1; i <= 5; i++) {
        for(j = 1; j <= i; j++) {
            printf("* ");
        }
        printf("\\n");
    }
    return 0;
}""",

    "Prog 6 — Pascal's triangle": """\
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

    "Prog 7 — Star pyramid": """\
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

    "Prog 8 — Palindrome check": """\
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

    "Prog 9 — While counter": """\
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

    "Prog 10 — Sum of digits": """\
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

    "Prog 11 — Reverse number": """\
#include <stdio.h>
int main() {
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
int main() {
    int i = 1;
    while(i <= 5) {
        printf("Number: %d\\n", i);
        i++;
    }
    printf("Loop Ended");
    return 0;
}""",

    "Prog 13 — Char classify": """\
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

    "Prog 14 — Largest of 3": """\
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

    "Prog 15 — Grade system": """\
#include <stdio.h>
int main() {
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

    "Prog 16 — Income tax": """\
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

    "Prog 17 — Leap year": """\
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

    "Prog 18 — Even/Odd Positive/Negative": """\
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

    "Prog 19 — Two positives check": """\
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

    "Prog 20 — Positive/Negative v2": """\
#include <stdio.h>
int main() {
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

    "Prog 21 — Login access control": """\
#include <stdio.h>
int main() {
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
}

SEP = "═" * 70
SEP2 = "─" * 70


def compile_and_report(name, src, show_tree=False, show_tokens=False):
    print(f"\n{SEP}")
    print(f"  {name}")
    print(SEP2)

    tokens, lex_errors = tokenize(src)
    tree, _, _, parse_err = parse(src)

    tok_types = {}
    for t in tokens:
        tok_types[t.type] = tok_types.get(t.type, 0) + 1

    print(f"  Tokens   : {len(tokens)}")
    for ttype, cnt in sorted(tok_types.items()):
        print(f"             {ttype:<20} x{cnt}")

    if lex_errors:
        print(f"  Lex Errs : {len(lex_errors)}")
        for e in lex_errors:
            print(f"    ⚠  {e}")
    else:
        print(f"  Lex      : ✓ OK")

    if parse_err:
        print(f"  Parser   : ✗ FAILED — {parse_err}")
    else:
        print(f"  Parser   : ✓ OK — parse tree generated")

    if show_tokens and tokens:
        print(f"\n  {'#':<4}{'LINE':<6}{'LEXEME':<18}{'TYPE':<16}PATTERN")
        print("  " + "─" * 70)
        for i, t in enumerate(tokens, 1):
            print(f"  {i:<4}{t.line:<6}{t.lexeme:<18}{t.type:<16}{t.pattern[:30]}")

    if show_tree and tree:
        print("\n  Parse Tree:")
        for line in tree_to_text(tree):
            print("  " + line)

    return not parse_err


def main():
    args = sys.argv[1:]
    show_tree = "--tree" in args
    args = [a for a in args if not a.startswith("--")]

    if args:
        # compile a file
        path = args[0]
        if not os.path.isfile(path):
            print(f"File not found: {path}")
            sys.exit(1)
        src = open(path).read()
        ok = compile_and_report(path, src, show_tree=True, show_tokens=True)
        sys.exit(0 if ok else 1)

    # test all 21 samples
    print("\n" + "█" * 70)
    print("  MINI C COMPILER — Testing all 21 sample programs")
    print("█" * 70)

    passed = failed = 0
    for name, src in SAMPLES.items():
        ok = compile_and_report(name, src, show_tree=show_tree)
        if ok: passed += 1
        else:  failed += 1

    print(f"\n{SEP}")
    print(f"  RESULTS:  {passed} passed  /  {failed} failed  /  {passed+failed} total")
    print(SEP)
    if failed == 0:
        print("  ✅ ALL PROGRAMS PARSED SUCCESSFULLY")
    else:
        print(f"  ❌ {failed} program(s) failed")
    print()


if __name__ == "__main__":
    main()
