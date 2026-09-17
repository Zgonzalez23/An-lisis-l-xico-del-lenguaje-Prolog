% programa_errores.pl - multiples errores lexicos recuperables
% El lexer debe reportar cada error con linea:col y continuar
padre(juan, ana).
'Atomo sin cierre
padre(juan, pedro).
X = "cadena sin cierre
Y is 3.x.
Z is 1e.
a.b.
padre(juan).extra.
precio@juan.
a : b.
c ? d.
e \ f.
/* bloque sin cierre
abuelo(X, Z) :- padre(X, Y).
