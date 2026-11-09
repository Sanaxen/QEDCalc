# VP05 sector202 A/B exact reduction pilot (2026-11-09)

This pilot is **not** a claim of proof. The 389/389 source-equation checkpoint completed with rank 389 and dependent 0; user reported successful exact pivot/source replay. The A/B target relations remain unproved.

## Environment

Windows 11; existing QEDCalc Python + SymPy environment; existing local Kira database and `output/tools/pyred_weight.py`. This runner does not invoke Kira or Fermat.

Expected local files:
- `output/three_loop_integral_family_audit/vp05_sector202_exact_support_checkpoint_support400_col256.json`
- `output/three_loop_integral_family_audit/vp05_sector202_exact_source_rows.json.gz`
- `output/three_loop_integral_family_audit/vp05_sector202_modular_provenance_certificate.json`

## Commands (from QEDCalc root)

First run A finite-field diagnostic (not an exact proof):

```powershell
.\run_vp05_sector202_target_exact_reduction.bat --target A --mode modular --max-steps 16 --output output/three_loop_integral_family_audit/vp05_sector202_A_modular_pilot.json
```

Then bounded exact-symbolic A pilot:

```powershell
.\run_vp05_sector202_target_exact_reduction.bat --target A --mode exact --max-steps 16 --max-columns 256 --max-support 400 --max-expression-chars 7500 --output output/three_loop_integral_family_audit/vp05_sector202_A_exact_pilot.json
```

For B, use `--target B` and distinct output filenames. A step/cap/unresolved result does not prove or disprove the relation. Existing result files are never overwritten.

## Mathematical scope and proof gate

A/B targets use the forms defined in `three_loop_vp05_sector202_symbolic_source_preflight.py`: `A-a(z,d)C-b(z,d)small4` and `B-c(z,d)C-e(z,d)small4`, with candidate rational functions from `three_loop_vp05_sector202_bivariate_candidate_verify.py`. Column `(4,73)` remains an *opaque* Kira column, not an independently identified physical master.

The exact pilot reduces targets using the saved source-provenance pivot basis. Exact proof for an individual target requires both an identically zero symbolic remainder and an independent exact replay of the target using original exported IBP rows. Modular specializations are diagnostics only.

## Validation limitations

Syntax/synthetic tests were performed for the original pilot. The user-local 389-pivot input, source export and Kira DB were unavailable here, so no end-to-end A/B proof has been run. GitHub commit records preserve the pilot; install via `git pull` on `feature/master-basis-initiate-only`.
