1 REM *** Print chars ***
2 INPUT "Introduce tamaño (0 para finalizar): "; t
3 IF t = 0 THEN STOP
4 INPUT "Introduce caracter: "; c$
10 REM *** Outer loop ***
20 FOR f = t TO 1 STEP -1 : LET f2 = t - f + 1 : PRINT f2; " ";
30 REM *** Inner loop ***
40 FOR c = f2 TO 1 STEP -1 : PRINT c$; : NEXT c
50 PRINT ""
60 NEXT f
70 PRINT "" : GO TO 1
