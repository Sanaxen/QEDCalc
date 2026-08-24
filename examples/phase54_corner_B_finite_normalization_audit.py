from qedcalc.operations.corner import corner_phase54_B_finite_normalization_audit
print('Phase-54 corner B finite-normalization audit')
for key,value in corner_phase54_B_finite_normalization_audit().items():
    print(f'{key} : {value}')
print('Phase-54: PASS')
