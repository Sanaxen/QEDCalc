import sympy as sp
from qedcalc.operations.corner import corner_eq32_operator_bridge
b=corner_eq32_operator_bridge()
for nu,M in enumerate(b.operator_residuals):
 print('nu',nu)
 for i,e in enumerate(M):
  if e!=0:
   print(i,sp.factor(e));break
