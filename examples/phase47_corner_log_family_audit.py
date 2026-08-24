from qedcalc.operations.corner import corner_phase47_log_family_audit
print('Phase-47 corner log-family denominator cancellation')
for k,v in corner_phase47_log_family_audit().items():
    print(k,':',v)
assert corner_phase47_log_family_audit()['scalar_identity_residual'] == 0
print('Phase-47: PASS')
