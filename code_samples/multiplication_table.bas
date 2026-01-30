10 FOR n = 1 TO 10
20 GO SUB 100
30 NEXT n
40 STOP
100 PRINT "Multiplication table of "; n
110 FOR m = 1 TO 10
120 PRINT m; " x "; n; " = "; m*n
130 NEXT m
140 PRINT ""
150 RETURN
