from qedcalc.operations.corner import corner_phase61_joint_soft_triangle_audit

print('Phase-61 corner finite-triangle joint-soft audit')
for k,v in corner_phase61_joint_soft_triangle_audit().items():
    print(f'{k}: {v}')
print('Phase-61: PASS')
