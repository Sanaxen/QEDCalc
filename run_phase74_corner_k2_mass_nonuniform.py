from qedcalc.operations.corner import corner_phase74_k2_mass_residual_nonuniform_audit, corner_phase74_rational_route_gap_qmc
print('Phase-74 exact non-uniform audit')
for k,v in corner_phase74_k2_mass_residual_nonuniform_audit().items(): print(k, '=', v)
for rho in (0.05,0.02,0.01):
    print('rho',rho,corner_phase74_rational_route_gap_qmc(rho,power=8,seed=11,replicates=4))
