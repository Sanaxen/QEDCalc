import sympy as sp
from qedcalc.operations.corner import corner_outer_common_quotients
q=corner_outer_common_quotients();k=q.k

def stream(poly,n,shift,A,C):
 pp=sp.Poly(sp.expand(poly),*k,domain='EX');out=0;metric=(1,-1,-1,-1)
 for mon,coef in pp.terms():
  e0=mon[0]
  for j0 in range(e0+1):
   if j0%2: continue
   exps=(j0,)+mon[1:]
   if any(ex%2 for ex in exps[1:]): continue
   rh=sum(exps)//2
   ga=n-rh-2
   anum=1
   for axis,ex in enumerate(exps):
    s=ex//2
    if s:
      anum*=sp.factorial2(2*s-1)*metric[axis]**s
   aden=1
   for j in range(rh):aden*=4+2*j
   angular=anum/aden
   binom=sp.binomial(e0,j0)*sp.I**j0*shift**(e0-j0)
   gf=sp.gamma(ga) if ga>0 else sp.Symbol(f'P{ga}')
   radial=sp.gamma(rh+2)*gf/sp.gamma(n)*A**(-2-rh)*C**(2+rh-n)
   out+=coef*binom*angular*radial
 return sp.factor(out)
ad,rho,X=sp.symbols('a_d rho X',positive=True);Q0=ad**2+(1-ad)*rho**2
T=stream(q.log_quotient,3,ad,1,Q0);print('T raw',T)
for p in list(T.free_symbols):
 if p.name.startswith('P'):
  print('pole',p,sp.factor(sp.expand(T).coeff(p)));T=sp.expand(T).subs(p,0)
T=sp.factor(T);G=sp.factor(2*ad*T)
known=X**2*(1-X)/(X**2+rho**2*(1-X))
print('T',T);print('ratio',sp.factor(sp.cancel(G.subs(ad,X)/known)))
