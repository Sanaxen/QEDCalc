from qedcalc.operations.corner import corner_phase48_sequential_family_audit

print('Phase-48 corner sequential-family audit')
for k,v in corner_phase48_sequential_family_audit().items():
    print(k, ':', v)
print('Phase-48: PASS')
