% programa_ok.pl - sin errores, cubre todas las categorias lexicas
/* Bloque:
   hechos, reglas, listas, aritmetica y DCG */
padre(juan, ana).
padre(juan, pedro).
padre('Juan Pérez', ana).
abuelo(X, Z) :-
    padre(X, Y),
    padre(Y, Z).
edad(juan, 42).
pi_valor(3.14).
exp_valor(1e-3).
saludo("hola mundo").
etiqueta(':-').
oracion --> sujeto, predicado.
sujeto --> [juan].
calc(X) :-
    X is 3 + 4 * 2 / 2 - 7 // 2,
    Y is 2 ** 3 mod 3,
    X =< Y,
    X >= 0,
    X \= 99,
    X == X,
    X \== Y,
    T =.. [p, 1, 2],
    \+ X = Y,
    ( X < 10 ; X > 100 ),
    !.
lista_ej([1, 2, 3]).
cabeza([H|T], H).
vacia([]).
anon(_, _Temporal, Persona).
llaves({a, b}).
?- abuelo(juan, Quien).
