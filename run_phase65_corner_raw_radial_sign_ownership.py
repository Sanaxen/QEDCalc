from qedcalc.operations.corner import corner_phase65_raw_radial_sign_ownership_audit

a=corner_phase65_raw_radial_sign_ownership_audit()
print('Phase-65 corner raw-radial sign ownership')
for k,v in a.items():
    print(k, ':', v)
ok=(a['scalar_n3_residual']==0 and a['raw_log_sign']==1 and a['raw_C_sign']==-1 and a['physical_bridge_C_sign']==1)
print('Phase-65:', 'PASS' if ok else 'FAIL')
raise SystemExit(0 if ok else 1)
