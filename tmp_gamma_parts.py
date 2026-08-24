import sympy as sp
from qedcalc.operations.corner import corner_outer_projector_streams
s=corner_outer_projector_streams();k=s.k
print('base=',sp.factor(s.log_base));print('trans=',sp.factor(s.log_transverse))
k2=k[0]**2-k[1]**2-k[2]**2-k[3]**2;D=sp.expand(k2-2*k[0])
for c in [4,-4,2,-2,1,-1]:
 common=sp.expand(D*s.log_base+c*sp.I*k[1]*s.log_transverse)
 q,r=sp.div(sp.Poly(common,*k,domain='EX'),sp.Poly(D,*k,domain='EX'))
 print('c',c,'q',sp.factor(q.as_expr()),'r',sp.factor(r.as_expr()))
