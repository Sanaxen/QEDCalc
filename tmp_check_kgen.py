import sympy as sp
from qedcalc.operations.corner import corner_raw_inner_vertex_finite_bridge,_corner_explicit_gamma_data
raw=corner_raw_inner_vertex_finite_bridge(); gu,gl=_corner_explicit_gamma_data();u,v=raw.u,raw.v;k=raw.k
f=1-u-sp.Rational(1,2)*u**2
for nu in range(4):
 K=sp.expand(raw.constant_matrices[nu]/2-2*f*gl[nu])
 # gamma_nu trace projection (using gamma^nu?)
 proj=sp.expand(sp.trace(gu[nu]*K)/4)
 print('nu',nu,'proj=',sp.factor(proj))
