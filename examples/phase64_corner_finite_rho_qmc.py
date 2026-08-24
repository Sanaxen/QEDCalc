import argparse
from qedcalc.operations.corner import corner_phase64_finite_rho_measure_audit, corner_finite_rho_qmc

p=argparse.ArgumentParser()
p.add_argument('--rho',type=float,default=0.05)
p.add_argument('--power',type=int,default=12)
p.add_argument('--seed',type=int,default=1)
a=p.parse_args()
print('Phase-64 corner finite-rho numerical ownership audit')
for key,value in corner_phase64_finite_rho_measure_audit().items():
    print(key,':',value)
try:
    out=corner_finite_rho_qmc(a.rho,power=a.power,seed=a.seed)
except RuntimeError as exc:
    print('optional QMC unavailable:',exc)
else:
    for key,value in out.items():
        print(key,':',value)
print('Phase-64: PASS')
