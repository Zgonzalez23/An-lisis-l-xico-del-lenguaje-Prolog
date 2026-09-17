import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from scanner import Lexer
from tokens import format_token


def main(argv):
    if len(argv) not in (2, 3) or (len(argv) == 3 and argv[2] != "--tabla"):
        print("Uso: python3 src/lexer.py <archivo.pl> [--tabla]", file=sys.stderr)
        return 2
    path = argv[1]
    show_tabla = len(argv) == 3
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"No existe: {path}", file=sys.stderr)
        return 2
    lx = Lexer(text)
    toks, errs, tab = lx.lex()
    for t in toks:
        print(format_token(t))
    if errs:
        print("--- errores ---")
        for e in errs:
            print(e)
    if show_tabla:
        d = tab.dump()
        print("--- tabla ---")
        for seccion in ("atomos", "variables", "literales"):
            print(f"{seccion}:")
            for i, lex in enumerate(d[seccion]):
                print(f"  {i}: '{lex}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
