from qedcalc.operations.corner import corner_phase50_K_convention_resolved_audit

a=corner_phase50_K_convention_resolved_audit()
print('Phase-50 KK/current K_nu convention-resolved audit')
for k,v in a.items():
    print(f'{k} : {v}')
ok=(a['null_base']==0 and a['null_transverse']==0 and a['base_residual']==0 and
    a['transverse_residual']==0 and a['common_residual']==0 and
    a['mapped_odd_is_transverse_odd'] and a['mapped_odd_has_k1k2_factor'])
print('Phase-50:', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
