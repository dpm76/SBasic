5 RANDOMIZE
10 FOR m = 1 TO 6: REM Seis lanzamientos
20 LET c = 0: REM Inicializar total a 0
30 FOR n = 1 TO 3: REM Para 3 monedas
40 LET c = c + 2 + INT (2 * RND)
50 NEXT n
60 PRINT "   ";
70 FOR n = 1 TO 2: REM Primero para el hexagrama, segundo para los cambios
80 PRINT "---";
90 IF c = 7 THEN PRINT "-";
100 IF c = 8 THEN PRINT " ";
110 IF c = 6 THEN PRINT "X";: LET c = 7
120 IF c = 9 THEN PRINT "0";: LET c = 8
130 PRINT "--- ";
140 NEXT n
150 PRINT
160 INPUT a$
170 NEXT m
