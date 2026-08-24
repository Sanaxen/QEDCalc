import sympy as sp
from qedcalc.operations.corner import (
    corner_gaussian_bare_templates,
    corner_uv_residue_sample,
    corner_local_uv_residue_sample,
    corner_uv_subtracted_residue_sample,
)

print('Phase-35 corner streaming Gaussian + local B-gamma UV bridge')
r=corner_gaussian_bare_templates()
print('G4 compact-template operations:',sp.count_ops(r.G4))
print('G5 compact-template operations:',sp.count_ops(r.G5))
X=sp.Rational(2,5);Y=sp.Rational(1,4);Z=sp.Rational(1,3);rho=sp.Rational(1,7)
expected=sp.Rational(1,2)*X**2*(1-X)/(X**2+rho**2*(1-X))
for d in (4,5):
    bare=corner_uv_residue_sample(d,X,Y,Z,rho)
    uv=corner_local_uv_residue_sample(d,X,Y,Z,rho)
    sub=corner_uv_subtracted_residue_sample(d,X,Y,Z,rho)
    print(f'diagram {d}: bare UV residue =',bare)
    print(f'diagram {d}: local B-gamma residue =',uv)
    print(f'diagram {d}: subtracted residue =',sub)
    assert sp.simplify(bare-expected)==0
    assert sp.simplify(uv-expected)==0
    assert sub==0
print('Phase-35 corner streaming Gaussian + local B-gamma UV bridge: PASS')
