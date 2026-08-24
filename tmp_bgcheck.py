import sympy as sp
from qedcalc.operations.corner import corner_physical_parameter_kernels
p=corner_physical_parameter_kernels(); u,rho,ad=p.symbols_B
expr=sp.factor(p.B_gamma)
print('expr=',expr)
res=sp.factor(sp.integrate(expr,(ad,0,1)))
print('int=',res)
X=sp.symbols('X', positive=True)
A1=sp.integrate(X**2*(1-X)/(X**2+rho**2*(1-X)),(X,0,1))
f=1-u-sp.Rational(1,2)*u**2;L0=u**2+rho**2*(1-u)
print('target formal factor=',sp.factor(-2*f/L0))
# Compare integrand-level Schwinger kernel under X=1-ad or ad?
for sub,name in [(1-X,'ad=1-X'),(X,'ad=X')]:
 bgX=sp.factor(expr.subs(ad,sub))
 target=sp.factor(-2*f/L0*X**2*(1-X)/(X**2+rho**2*(1-X)))
 print(name,'ratio=',sp.factor(sp.cancel(bgX/target)))
