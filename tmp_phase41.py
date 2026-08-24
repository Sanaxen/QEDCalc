import sympy as sp
from qedcalc.operations.corner import corner_outer_projector_streams
s=corner_outer_projector_streams(); k=s.k
k2=k[0]**2-k[1]**2-k[2]**2-k[3]**2
D=sp.expand(k2-2*k[0])
for name,b,t in [('log',s.log_base,s.log_transverse),('lp',s.lp_base,s.lp_transverse),('l0',s.l0_base,s.l0_transverse)]:
    for sign in [1,-1]:
      common=sp.expand(D*b + sign*4*sp.I*k[1]*t)
      P=sp.Poly(common,*k,domain='EX'); div=sp.div(P,sp.Poly(D,*k,domain='EX'))
      q,r=div
      terms=list(r.terms())
      print(name,sign,'qterms',len(q.terms()),'rterms',len(terms),'r=',sp.factor(r.as_expr()))
