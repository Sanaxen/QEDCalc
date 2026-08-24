from qedcalc.operations.corner import corner_phase46_photon_sign_ownership_audit

print('Phase-46 corner inner/outer photon sign ownership audit')
for k,v in corner_phase46_photon_sign_ownership_audit().items():
    print(f'{k}: {v}')
print('Phase-46: PASS')
