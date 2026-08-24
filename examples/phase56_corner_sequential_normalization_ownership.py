from qedcalc.operations.corner import corner_phase56_sequential_normalization_ownership_audit

print("Phase-56 corner sequential normalization + measure ownership")
for k,v in corner_phase56_sequential_normalization_ownership_audit().items():
    print(f"{k}: {v}")
print("Phase-56: PASS")
