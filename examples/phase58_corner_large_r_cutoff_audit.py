from qedcalc.operations.corner import corner_phase58_large_r_cutoff_audit

a=corner_phase58_large_r_cutoff_audit()
print('Phase-58 corner large-r cutoff ownership audit')
for k,v in a.items():
    print(k, ':', v)
ok=(a['log_coefficient_residual']==0)
print('Phase-58:', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
