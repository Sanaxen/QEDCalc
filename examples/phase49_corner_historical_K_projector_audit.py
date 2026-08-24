from qedcalc.operations.corner import corner_phase49_historical_K_projector_audit

r=corner_phase49_historical_K_projector_audit()
print('Phase-49 historical K_nu projector regeneration')
for k,v in r.items():
    print(f'{k} : {v}')
ok=(r['common_division_residual']==0 and r['odd_remainder_is_transverse_odd'] and r['odd_remainder_has_k1k2_factor'])
print('Phase-49:', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
