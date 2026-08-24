import sympy as sp
from qedcalc.operations.corner import corner_outer_common_quotients,_corner_gaussian_template
q=corner_outer_common_quotients();k=q.k
T,S,A,C=_corner_gaussian_template(q.log_quotient,3,k)
ad,rho=sp.symbols('a_d rho', positive=True)
Q0=ad**2+(1-ad)*rho**2
G=sp.factor(2*ad*T.subs({S:ad,A:1,C:Q0}))
X=sp.symbols('X', positive=True)
known=X**2*(1-X)/(X**2+rho**2*(1-X))
print('T=',sp.factor(T))
print('G=',G)
print('ratio ad=X=',sp.factor(sp.cancel(G.subs(ad,X)/known)))
