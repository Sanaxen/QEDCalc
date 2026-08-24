from qedcalc.operations.corner import corner_phase72_full_stabilized_audit, corner_phase72_full_stabilized_qmc
for k,v in corner_phase72_full_stabilized_audit().items():
    print(f'{k}: {v}')
for rho in (0.05,0.02,0.01,0.005,0.002):
    print(f'--- rho={rho} ---')
    for k,v in corner_phase72_full_stabilized_qmc(rho,power=10,seed=7,replicates=4).items():
        print(f'{k}: {v}')
print('Phase-72: PASS')
