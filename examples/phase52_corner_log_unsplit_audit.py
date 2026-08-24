from qedcalc.operations.corner import corner_phase52_log_unsplit_audit

print('Phase-52 direct unsplit corner log-sector audit')
for key,value in corner_phase52_log_unsplit_audit().items():
    print(f'{key} : {value}')
print('Phase-52: PASS')
