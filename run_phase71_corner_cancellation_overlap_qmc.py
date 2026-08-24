from qedcalc.operations.corner import (
    corner_phase71_cancellation_first_overlap_measure_audit,
    corner_cancellation_first_overlap_qmc,
)

for k,v in corner_phase71_cancellation_first_overlap_measure_audit().items():
    print(f'{k}: {v}')
for rho in (0.05,0.02,0.01):
    print(f'--- rho={rho} ---')
    out=corner_cancellation_first_overlap_qmc(rho,power=10,seed=7,replicates=4)
    for k,v in out.items():
        print(f'{k}: {v}')
print('Phase-71: PASS')
