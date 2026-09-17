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

    def dump(self) -> dict[str, list[str]]:
        """Listas ordenadas por indice para mostrar con --tabla."""
        return {
            "atomos": list(self._order_atom),
            "variables": list(self._order_var),
            "literales": list(self._order_lit),
        }
