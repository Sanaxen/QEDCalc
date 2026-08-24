from qedcalc.operations.corner import corner_phase45_eq32_operator_audit
r=corner_phase45_eq32_operator_audit()
print('Phase-45 corner Eq32 operator + Schwinger calibration')
for k,v in r.items(): print(f'{k}: {v}')
assert r['eq32_operator_zero_flags'] == (True,True,True,True)
assert r['schwinger_raw_ratio'] == -4
assert r['schwinger_after_eq42_quarter_ratio'] == -1
print('Phase-45: PASS')
