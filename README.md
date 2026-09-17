# Análisis Léxico del lenguaje Prolog

Analizador léxico para un subconjunto de Prolog (inspirado en ISO Prolog y SWI-Prolog).
Recorre archivos fuente de izquierda a derecha y produce una secuencia ordenada de tokens.

**Alcance:** solo análisis léxico. No sintaxis, no árboles, no validación gramatical.
**Lenguaje:** Python

## Estructura
```
src/                # analizador (tipo, lexema, línea, columna + tabla de lexemas + errores)
tests/
  validos/          # >=20 pruebas válidas, todas las categorías
  invalidos/        # >=8 pruebas inválidas (cierre, caracteres, números)
  completos/        # 1 archivo sin errores + 1 con múltiples errores recuperables
```

## Salida esperada por token
`<TIPO, 'lexema', linea, columna>` — línea y columna 1-indexadas.
Ejemplo: `<ATOMO, 'padre', 2, 1>`

## Cómo ejecutar
```bash
python3 src/lexer.py tests/completos/programa_ok.pl
python3 src/lexer.py tests/completos/programa_errores.pl
python3 src/lexer.py <archivo.pl> --tabla   # + tabla atomos/variables/literales
```

## Corpus reproducible
```bash
python3 tests/run_tests.py            # resumen (exige 0 errores en validos/ok)
python3 tests/run_tests.py --verbose  # + tokens y errores por archivo
```
- `tests/validos/` (21): v01_atomos … v21_escapes; incluye v18 máxima
  coincidencia (`a:-b.`, `X==Y`, `\==` vs `\=`, `=..`, `//` vs `/`, `**` vs `*`,
  `-->` vs `-`, `\+`) y v19 prioridad (`is`/`mod` vs `island`/`mod2`/`is_1`).
- `tests/invalidos/` (10): e01–e02 átomo sin cierre (salto/EOF), e03–e04 cadena
  sin cierre (salto/EOF), e05 bloque sin cierre, e06 caracteres no admitidos
  (`@ # $ & \` ~`), e07 punto sin decimales (`3.x`), e08 exponente sin dígitos
  (`1e`, `2E+`), e09 punto mal ubicado (`a.b`), e10 `:`/`?`/`\` aislados.
- `tests/completos/`: `programa_ok.pl` (0 errores, 39/39 tipos) y
  `programa_errores.pl` (11 errores recuperables, sigue emitiendo tokens).

## Convenciones fijadas
- [x] signo `-` siempre operador separado, nunca parte del número
- [x] escapes: `'...'` con `''` + `\' \\ \n \t \r`; `"..."` con `\" \\ \n \t \r`
- [x] `/* ... */` no anidado, primer `*/` cierra
- [x] `.` final solo si va seguido de blanco/salto/`%`/`/*`/EOF
- [x] prioridad `is`/`mod` como palabra completa + máxima coincidencia
