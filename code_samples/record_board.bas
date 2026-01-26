10 INPUT "string"; a$: CLS
20 FOR s=0 TO 18 STEP 2
30 FOR a=LEN a$ TO 1 STEP -1: PRINT AT s,0; a$(a TO LEN a$)
40 NEXT a
100 IF LEN a$=31 THEN PRINT AT 10,8; "string too long": GO TO 10
110 FOR a=LEN a$ TO 0 STEP -1
120 PRINT AT s+1,0; TAB (a); a$ (1 TO LEN a$);" "
130 NEXT a
140 NEXT s