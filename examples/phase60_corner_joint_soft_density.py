from qedcalc.operations.corner import corner_phase60_joint_soft_density_audit

d=corner_phase60_joint_soft_density_audit()
print('Phase-60 corner joint soft-density normalization')
for k,v in d.items():
    print(f'{k}: {v}')
ok=(d['S_integral_residual']==0 and d['normalization_residual']==0 and d['R_integral']==1)
print('Phase-60:', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
