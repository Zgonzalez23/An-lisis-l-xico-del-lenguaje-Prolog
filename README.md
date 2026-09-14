# Análisis Léxico del lenguaje Prolog

Analizador léxico para un subconjunto de Prolog (inspirado en ISO Prolog y SWI-Prolog).
Recorre archivos fuente de izquierda a derecha y produce una secuencia ordenada de tokens.

**Alcance:** solo análisis léxico. No sintaxis, no árboles, no validación gramatical.
**Lenguaje:** Python

## Estructura
```
docs/               # especificación, regex, autómatas, determinización/minimización
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
_Pendiente Fase 5: definir CLI final y formato de errores._

## Convenciones fijadas (Fase 1 pendiente)
- [ ] signo `-` es operador separado vs parte de número
- [ ] escapes en `'...'` y `"..."`
- [ ] `/* ... */` anidado o no
- [ ] `.` final solo si va seguido de blanco/salto/fin
- [ ] prioridad `is`/`mod` y máxima coincidencia
