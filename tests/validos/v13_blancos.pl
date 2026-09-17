% v13: blancos (espacios, tabs, saltos) se ignoran
padre(   juan,	ana   )   .


abuelo( X , Z ) :-
	padre( X , Y ) ,
	padre( Y , Z ) .
