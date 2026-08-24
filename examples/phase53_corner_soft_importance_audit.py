from qedcalc.operations.corner import corner_phase53_soft_importance_audit

print('Phase-53 corner soft-importance map audit')
for key,value in corner_phase53_soft_importance_audit().items():
    print(f'{key} : {value}')
print('Phase-53: PASS')
