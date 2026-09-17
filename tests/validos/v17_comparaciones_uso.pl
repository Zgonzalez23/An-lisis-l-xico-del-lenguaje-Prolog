% v17: comparaciones en cuerpos
mayor(X, Y) :- X > Y.
menor_igual(X, Y) :- X =< Y.
igual(X, X).
distinto(X, Y) :- X \== Y.
no_unifica(X, Y) :- X \= Y.
descomp(T) :- T =.. [F|Args].
