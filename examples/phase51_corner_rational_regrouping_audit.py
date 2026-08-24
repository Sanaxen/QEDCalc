from qedcalc.operations.corner import corner_phase51_rational_regrouping_audit

a=corner_phase51_rational_regrouping_audit()
print('Phase-51 corner rational regrouping audit')
for k,v in a.items():
    print(f'{k} : {v}')
def z(x):
    if isinstance(x,tuple): return all(z(y) for y in x)
    return x==0
ok=all(z(v) for v in a.values())
print('Phase-51:', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
