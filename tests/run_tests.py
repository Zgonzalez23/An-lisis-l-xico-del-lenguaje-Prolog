import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "src"))

from scanner import Lexer

VALIDOS = os.path.join(ROOT, "tests", "validos")
INVALIDOS = os.path.join(ROOT, "tests", "invalidos")
COMPLETOS = os.path.join(ROOT, "tests", "completos")

TIPOS_ESPERADOS = {
    "ATOMO", "ATOMO_QUOTED", "VARIABLE", "VAR_ANONIMA",
    "ENTERO", "REAL", "CADENA",
    "OP_CLAUSULA", "OP_CONSULTA", "OP_DCG",
    "OP_UNIF", "OP_NO_UNIF", "OP_EQ", "OP_NEQ", "OP_UNIV",
    "OP_LT", "OP_LE", "OP_GT", "OP_GE",
    "OP_SUMA", "OP_RESTA", "OP_MULT", "OP_DIV", "OP_DIVENT", "OP_POT",
    "OP_IS", "OP_MOD",
    "OP_NOT", "OP_CUT", "OP_PUNTOYCOMA", "COMA",
    "PARENTESIS_IZQ", "PARENTESIS_DER",
    "CORCH_IZQ", "CORCH_DER", "LLAVE_IZQ", "LLAVE_DER",
    "BARRA", "PUNTO",
}


def lex_file(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lx = Lexer(text)
    return lx.lex()


def main():
    verbose = "--verbose" in sys.argv
    fallos = []
    vistos = set()

    validos = sorted(f for f in os.listdir(VALIDOS) if f.endswith(".pl"))
    invalidos = sorted(f for f in os.listdir(INVALIDOS) if f.endswith(".pl"))
    print(f"validos: {len(validos)} archivos (minimo 20)")
    print(f"invalidos: {len(invalidos)} archivos (minimo 8)")
    if len(validos) < 20:
        fallos.append(f"validos insuficientes: {len(validos)} < 20")
    if len(invalidos) < 8:
        fallos.append(f"invalidos insuficientes: {len(invalidos)} < 8")

    for name in validos:
        toks, errs, _ = lex_file(os.path.join(VALIDOS, name))
        vistos.update(t.tipo for t in toks)
        estado = "OK " if not errs else "FALLO"
        print(f"  [{estado}] validos/{name}: {len(toks)} toks, {len(errs)} errs")
        if verbose:
            for t in toks:
                print(f"      <{t.tipo}, '{t.lexema}', {t.linea}, {t.col}>")
            for e in errs:
                print(f"      {e}")
        if errs:
            fallos.append(f"validos/{name} debia tener 0 errores, tuvo {len(errs)}")

    for name in invalidos:
        toks, errs, _ = lex_file(os.path.join(INVALIDOS, name))
        vistos.update(t.tipo for t in toks)
        estado = "OK " if errs else "FALLO"
        print(f"  [{estado}] invalidos/{name}: {len(toks)} toks, {len(errs)} errs")
        if verbose:
            for e in errs:
                print(f"      {e}")
        if not errs:
            fallos.append(f"invalidos/{name} debia tener >=1 error, tuvo 0")

    # Completos
    toks_ok, errs_ok, _ = lex_file(os.path.join(COMPLETOS, "programa_ok.pl"))
    vistos.update(t.tipo for t in toks_ok)
    print(f"  [{'OK ' if not errs_ok else 'FALLO'}] completos/programa_ok.pl: "
          f"{len(toks_ok)} toks, {len(errs_ok)} errs")
    if errs_ok:
        fallos.append(f"programa_ok.pl debia tener 0 errores, tuvo {len(errs_ok)}")
        for e in errs_ok:
            print(f"      {e}")

    toks_e, errs_e, _ = lex_file(os.path.join(COMPLETOS, "programa_errores.pl"))
    ok_err = len(errs_e) >= 5 and len(toks_e) > 0
    print(f"  [{'OK ' if ok_err else 'FALLO'}] completos/programa_errores.pl: "
          f"{len(toks_e)} toks, {len(errs_e)} errs (esperado >=5 errs y >0 toks)")
    for e in errs_e:
        print(f"      {e}")
    if not ok_err:
        fallos.append("programa_errores.pl debe tener >=5 errores y >0 tokens (recuperacion)")

    faltan = TIPOS_ESPERADOS - vistos
    print(f"\ncobertura tipos: {len(vistos)}/{len(TIPOS_ESPERADOS)}")
    if faltan:
        print(f"  FALTAN: {sorted(faltan)}")
        fallos.append(f"tipos no cubiertos: {sorted(faltan)}")
    else:
        print("  todos los tipos del subconjunto aparecen en el corpus")

    # Chequeo rapido de maxima coincidencia / prioridad (v18+v19 deben ser limpios)
    for esp in ("v18_maxima_coincidencia.pl", "v19_prioridad_palabras.pl"):
        _, errs, _ = lex_file(os.path.join(VALIDOS, esp))
        if errs:
            fallos.append(f"{esp} (maxima coincidencia/prioridad) tuvo errores: {errs}")

    print()
    if fallos:
        print(f"FALLO: {len(fallos)} problema(s)")
        for f in fallos:
            print(f"  - {f}")
        return 1
    print("TODO OK: corpus reproducible valido")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
