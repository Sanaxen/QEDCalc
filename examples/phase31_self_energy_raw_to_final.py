from qedcalc.operations.self_energy import self_energy_raw_to_final_audit
r=self_energy_raw_to_final_audit()
print('Phase-31 self-energy raw-to-final audit')
print('Raw sample checks:',r.raw_sample_checks)
print('Raw UV archived difference:',r.raw_uv_archived_difference)
print('Renormalized G_A residual:',r.renormalized_GA_residual)
print('Finite A:',r.finite_A)
print('IR B:',r.ir_B)
print('Total:',r.total)
print('Final checkpoint residual:',r.total_checkpoint_residual)
ok=all(x==0 for x in r.raw_sample_checks) and r.raw_uv_archived_difference==0 and r.renormalized_GA_residual==0 and r.total_checkpoint_residual==0
print('Phase-31 self-energy raw-to-final audit: PASS' if ok else 'FAIL')
