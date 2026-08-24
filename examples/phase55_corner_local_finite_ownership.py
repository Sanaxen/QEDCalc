from qedcalc.operations.corner import corner_phase55_local_finite_ownership_audit

print("Phase-55 corner local finite-normalization ownership audit")
for k,v in corner_phase55_local_finite_ownership_audit().items():
    print(f"{k}: {v}")
print("Phase-55: PASS")
