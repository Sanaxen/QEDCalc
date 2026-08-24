from qedcalc.operations.corner import corner_phase57_large_r_overlap_audit

a=corner_phase57_large_r_overlap_audit()
print('Phase-57 corner large-r soft-overlap audit')
for k,v in a.items():
    print(k, ':', v)
ok=(a['large_r_residual']==0 and a['subtracted_one_over_r_residual']==0)
print('Phase-57:', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
