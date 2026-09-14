"""Analizador lexico para subconjunto Prolog (Fases 1-3).
Uso: python3 src/lexer.py <archivo.pl>
Emite <TIPO, 'lexema', linea, col> por token, tabla de lexemas y errores.
"""
import sys
from dataclasses import dataclass, field


@dataclass
class Token:
    tipo: str
    lexema: str
    linea: int
    col: int
    attr: object = None  # indice en tabla de lexemas o None


@dataclass
class LexError:
    linea: int
    col: int
    fragmento: str
    mensaje: str

    def __str__(self):
        frag = self.fragmento.replace("\n", "\\n")
        if len(frag) > 30:
            frag = frag[:30] + "..."
        return f"ERROR_LEXICO {self.linea}:{self.col} '{frag}' : {self.mensaje}"


class SymbolTable:
    """Registra atomos, variables y literales sin duplicados."""

    def __init__(self):
        self.atomos: dict[str, int] = {}
        self.variables: dict[str, int] = {}
        self.literales: dict[str, int] = {}
        self._order_atom: list[str] = []
        self._order_var: list[str] = []
        self._order_lit: list[str] = []

    def add_atomo(self, lex: str) -> int:
        if lex not in self.atomos:
            self.atomos[lex] = len(self._order_atom)
            self._order_atom.append(lex)
        return self.atomos[lex]

    def add_var(self, lex: str) -> int:
        if lex not in self.variables:
            self.variables[lex] = len(self._order_var)
            self._order_var.append(lex)
        return self.variables[lex]

    def add_lit(self, lex: str) -> int:
        if lex not in self.literales:
            self.literales[lex] = len(self._order_lit)
            self._order_lit.append(lex)
        return self.literales[lex]


def _is_digit(c: str) -> bool:
    return "0" <= c <= "9"


def _is_lower(c: str) -> bool:
    return "a" <= c <= "z"


def _is_upper(c: str) -> bool:
    return "A" <= c <= "Z"


def _is_alnum_us(c: str) -> bool:
    return _is_lower(c) or _is_upper(c) or _is_digit(c) or c == "_"


class Lexer:
    def __init__(self, text: str):
        # Normaliza saltos: \r\n y \r -> \n (cuenta como 1 salto)
        self.text = text.replace("\r\n", "\n").replace("\r", "\n")
        self.n = len(self.text)
        self.pos = 0
        self.linea = 1
        self.col = 1
        self.tokens: list[Token] = []
        self.errores: list[LexError] = []
        self.tabla = SymbolTable()

    # ---- utilidades de avance ----
    def peek(self, k: int = 0) -> str | None:
        i = self.pos + k
        return self.text[i] if 0 <= i < self.n else None

    def _advance_one(self) -> str | None:
        if self.pos >= self.n:
            return None
        c = self.text[self.pos]
        self.pos += 1
        if c == "\n":
            self.linea += 1
            self.col = 1
        else:
            self.col += 1  # \t cuenta como 1, documentado
        return c

    def _advance_n(self, k: int):
        for _ in range(k):
            self._advance_one()

    def _error(self, linea, col, frag, msg):
        self.errores.append(LexError(linea, col, frag, msg))

    # ---- bucle principal (q0 despachador, Fase 3 §7) ----
    def lex(self):
        while self.pos < self.n:
            c = self.text[self.pos]
            if c in " \t\n":
                self._advance_one()
                continue
            if c == "%":
                self._lex_line_comment()
                continue
            if c == "/" and self.peek(1) == "*":
                self._lex_block_comment()
                continue
            if c == "'":
                self._lex_quoted()
                continue
            if c == '"':
                self._lex_string()
                continue
            if _is_lower(c):
                self._lex_atomo()
                continue
            if _is_upper(c) or c == "_":
                self._lex_variable()
                continue
            if _is_digit(c):
                self._lex_numero()
                continue
            # operadores / delimitadores / errores
            self._lex_operador()
        return self.tokens, self.errores, self.tabla

    # ---- comentarios ----
    def _lex_line_comment(self):
        while self.pos < self.n and self.text[self.pos] != "\n":
            self._advance_one()
        # el \n queda para la siguiente iteracion (actualiza linea)

    def _lex_block_comment(self):
        l0, c0 = self.linea, self.col
        start = self.pos
        self._advance_n(2)  # /*
        while self.pos < self.n:
            if self.text[self.pos] == "*" and self.peek(1) == "/":
                self._advance_n(2)
                return
            self._advance_one()
        # EOF sin cierre
        frag = self.text[start:min(start + 30, self.n)]
        self._error(l0, c0, frag, "comentario de bloque sin cierre /* ... */")

    # ---- quoted / cadena ----
    def _lex_quoted(self):
        l0, c0 = self.linea, self.col
        start = self.pos
        self._advance_one()  # '
        while self.pos < self.n:
            c = self.text[self.pos]
            if c == "\n":
                frag = self.text[start:self.pos]
                self._error(l0, c0, frag, "atomo entre comillas sin cierre antes de salto")
                return  # no consume \n, sigue el bucle principal
            if c == "\\":
                nx = self.peek(1)
                if nx is not None and nx in "'\\nrt":
                    self._advance_n(2)
                else:
                    # escape invalido: se consume igual para poder continuar
                    self._advance_n(2 if nx is not None else 1)
                continue
            if c == "'":
                if self.peek(1) == "'":  # '' escapada
                    self._advance_n(2)
                    continue
                self._advance_one()  # cierre
                lex = self.text[start:self.pos]
                idx = self.tabla.add_atomo(lex)
                self.tokens.append(Token("ATOMO_QUOTED", lex, l0, c0, idx))
                return
            self._advance_one()
        frag = self.text[start:self.pos]
        self._error(l0, c0, frag, "atomo entre comillas sin cierre (EOF)")

    def _lex_string(self):
        l0, c0 = self.linea, self.col
        start = self.pos
        self._advance_one()  # "
        while self.pos < self.n:
            c = self.text[self.pos]
            if c == "\n":
                frag = self.text[start:self.pos]
                self._error(l0, c0, frag, "cadena sin cierre antes de salto")
                return
            if c == "\\":
                nx = self.peek(1)
                if nx is not None and nx in '"\\nrt':
                    self._advance_n(2)
                else:
                    self._advance_n(2 if nx is not None else 1)
                continue
            if c == '"':
                self._advance_one()
                lex = self.text[start:self.pos]
                idx = self.tabla.add_lit(lex)
                self.tokens.append(Token("CADENA", lex, l0, c0, idx))
                return
            self._advance_one()
        frag = self.text[start:self.pos]
        self._error(l0, c0, frag, "cadena sin cierre (EOF)")

    # ---- identificadores ----
    def _lex_atomo(self):
        l0, c0 = self.linea, self.col
        start = self.pos
        while self.pos < self.n and _is_alnum_us(self.text[self.pos]):
            self._advance_one()
        lex = self.text[start:self.pos]
        if lex == "is":
            self.tokens.append(Token("OP_IS", lex, l0, c0, None))
        elif lex == "mod":
            self.tokens.append(Token("OP_MOD", lex, l0, c0, None))
        else:
            idx = self.tabla.add_atomo(lex)
            self.tokens.append(Token("ATOMO", lex, l0, c0, idx))

    def _lex_variable(self):
        l0, c0 = self.linea, self.col
        start = self.pos
        while self.pos < self.n and _is_alnum_us(self.text[self.pos]):
            self._advance_one()
        lex = self.text[start:self.pos]
        if lex == "_":
            idx = self.tabla.add_var(lex)
            self.tokens.append(Token("VAR_ANONIMA", lex, l0, c0, idx))
        else:
            idx = self.tabla.add_var(lex)
            self.tokens.append(Token("VARIABLE", lex, l0, c0, idx))

    # ---- numeros ----
    def _lex_numero(self):
        l0, c0 = self.linea, self.col
        start = self.pos
        while self.pos < self.n and _is_digit(self.text[self.pos]):
            self._advance_one()
        es_real = False
        # parte fraccionaria: . + digito obligatorio
        if self.peek() == ".":
            nx = self.peek(1)
            nx2 = self.peek(2)
            if nx is not None and _is_digit(nx):
                es_real = True
                self._advance_one()  # .
                while self.pos < self.n and _is_digit(self.text[self.pos]):
                    self._advance_one()
            elif nx is None or nx in " \t\n" or nx == "%" or (nx == "/" and nx2 == "*"):
                # '2.' ante terminador = ENTERO(2) + PUNTO, no error.
                # Se emite el entero y se deja '.' para _lex_operador.
                lex = self.text[start:self.pos]
                idx = self.tabla.add_lit(lex)
                self.tokens.append(Token("ENTERO", lex, l0, c0, idx))
                return
            else:
                # '3.x', '3.,', '3.:-' etc -> malformado
                self._advance_one()  # consume .
                frag = self.text[start:self.pos]
                self._error(l0, c0, frag, "numero malformado: punto sin decimales fuera de fin de clausula")
                return
        # exponente: e/E [+-]? digitos obligatorios
        if self.peek() in ("e", "E"):
            p1 = self.peek(1)
            p2 = self.peek(2)
            if p1 is not None and _is_digit(p1):
                es_real = True
                self._advance_one()  # e
                while self.pos < self.n and _is_digit(self.text[self.pos]):
                    self._advance_one()
            elif p1 in ("+", "-") and p2 is not None and _is_digit(p2):
                es_real = True
                self._advance_n(2)  # e + signo
                while self.pos < self.n and _is_digit(self.text[self.pos]):
                    self._advance_one()
            else:
                # consume 'e' y signo si hay, reporta malformado, deja el resto
                self._advance_one()  # e
                if self.peek() in ("+", "-"):
                    self._advance_one()
                frag = self.text[start:self.pos]
                self._error(l0, c0, frag, "numero malformado: exponente sin digitos (ej '1e')")
                return
        lex = self.text[start:self.pos]
        idx = self.tabla.add_lit(lex)
        tipo = "REAL" if es_real else "ENTERO"
        self.tokens.append(Token(tipo, lex, l0, c0, idx))

    # ---- operadores / delimitadores ----
    def _lex_operador(self):
        l0, c0 = self.linea, self.col
        t = self.text
        p = self.pos
        rest3 = t[p:p + 3]
        rest2 = t[p:p + 2]
        c = t[p]

        def emit(tipo, k):
            lex = t[p:p + k]
            self._advance_n(k)
            self.tokens.append(Token(tipo, lex, l0, c0, None))

        # 3 chars primero (maxima coincidencia)
        if rest3 == "-->":
            return emit("OP_DCG", 3)
        if rest3 == "\\==":
            return emit("OP_NEQ", 3)
        if rest3 == "=..":
            return emit("OP_UNIV", 3)
        # 2 chars
        if rest2 == ":-":
            return emit("OP_CLAUSULA", 2)
        if rest2 == "?-":
            return emit("OP_CONSULTA", 2)
        if rest2 == "==":
            return emit("OP_EQ", 2)
        if rest2 == "\\=":
            return emit("OP_NO_UNIF", 2)
        if rest2 == "=<":
            return emit("OP_LE", 2)
        if rest2 == ">=":
            return emit("OP_GE", 2)
        if rest2 == "//":
            return emit("OP_DIVENT", 2)
        if rest2 == "**":
            return emit("OP_POT", 2)
        if rest2 == "\\+":
            return emit("OP_NOT", 2)
        # 1 char
        if c == "=":
            return emit("OP_UNIF", 1)
        if c == "<":
            return emit("OP_LT", 1)
        if c == ">":
            return emit("OP_GT", 1)
        if c == "+":
            return emit("OP_SUMA", 1)
        if c == "-":
            return emit("OP_RESTA", 1)
        if c == "*":
            return emit("OP_MULT", 1)
        if c == "/":
            return emit("OP_DIV", 1)
        if c == "!":
            return emit("OP_CUT", 1)
        if c == ";":
            return emit("OP_PUNTOYCOMA", 1)
        if c == ",":
            return emit("COMA", 1)
        if c == "(":
            return emit("PARENTESIS_IZQ", 1)
        if c == ")":
            return emit("PARENTESIS_DER", 1)
        if c == "[":
            return emit("CORCH_IZQ", 1)
        if c == "]":
            return emit("CORCH_DER", 1)
        if c == "{":
            return emit("LLAVE_IZQ", 1)
        if c == "}":
            return emit("LLAVE_DER", 1)
        if c == "|":
            return emit("BARRA", 1)
        if c == ".":
            # PUNTO solo ante blanco/%/ /* /EOF
            nx = self.peek(1)
            nx2 = self.peek(2)
            if nx is None or nx in " \t\n" or nx == "%" or (nx == "/" and nx2 == "*"):
                return emit("PUNTO", 1)
            self._advance_one()
            self._error(l0, c0, ".", "punto mal ubicado: debe ir seguido de blanco, % , /* o fin")
            return
        if c == ":":
            self._advance_one()
            self._error(l0, c0, ":", "operador incompleto: ':' aislado (se esperaba ':-')")
            return
        if c == "?":
            self._advance_one()
            self._error(l0, c0, "?", "operador incompleto: '?' aislado (se esperaba '?-')")
            return
        if c == "\\":
            self._advance_one()
            self._error(l0, c0, "\\", "barra invertida aislada (se esperaba \\=, \\== o \\+)")
            return
        # caracter no admitido (incluye no-ASCII fuera de quoted/cadena)
        self._advance_one()
        self._error(l0, c0, c, "caracter no admitido")


def format_token(t: Token) -> str:
    return f"<{t.tipo}, '{t.lexema}', {t.linea}, {t.col}>"


def main(argv):
    if len(argv) != 2:
        print("Uso: python3 src/lexer.py <archivo.pl>", file=sys.stderr)
        return 2
    path = argv[1]
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
