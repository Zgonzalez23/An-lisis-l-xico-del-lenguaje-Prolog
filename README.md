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
```

## Convenciones fijadas
- [x] signo `-` siempre operador separado, nunca parte del número
- [x] escapes: `'...'` con `''` + `\' \\ \n \t \r`; `"..."` con `\" \\ \n \t \r`
- [x] `/* ... */` no anidado, primer `*/` cierra
- [x] `.` final solo si va seguido de blanco/salto/`%`/`/*`/EOF
- [x] prioridad `is`/`mod` como palabra completa + máxima coincidencia
