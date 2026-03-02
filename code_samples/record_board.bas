10 INPUT "string? "; a$: CLS
20 FOR s=0 TO 18 STEP 2
30 FOR i=LEN a$ TO 1 STEP -1: PRINT AT s,0; STR$(s) + a$(i TO);: WAIT 0.15: NEXT i
110 REM FOR j=LEN a$ TO 0 STEP -1: PRINT AT s+1,j; STR$(s+1) + a$;" ";: WAIT 0.15: NEXT j
140 NEXT s