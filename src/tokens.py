from dataclasses import dataclass


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


def format_token(t: Token) -> str:
    return f"<{t.tipo}, '{t.lexema}', {t.linea}, {t.col}>"
