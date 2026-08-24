from qedcalc.operations.corner import corner_phase59_overlap_add_subtract_audit

d=corner_phase59_overlap_add_subtract_audit()
print('Phase-59 corner overlap add-subtract routing')
for k,v in d.items():
    print(f'{k}: {v}')
ok=(d['pointwise_recombination_residual']==0 and
    d['cutoff_addback_residual']==0 and
    d['subtracted_one_over_r_residual']==0)
print('Phase-59:', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
