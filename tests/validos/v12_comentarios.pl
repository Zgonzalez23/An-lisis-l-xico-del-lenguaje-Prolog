% comentario de linea solo
padre(juan, ana). % comentario al final
/* bloque en una linea */
padre(juan, pedro). /* otro */
/* bloque
   multilinea
   fin */
abuelo(X, Z) :- padre(X, Y).
/**/.
