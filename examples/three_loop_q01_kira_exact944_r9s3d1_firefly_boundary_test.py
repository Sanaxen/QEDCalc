"""Run/audit the Q01 exact944 d+1 seed-boundary extension with FireFly.

This helper reuses the validated r10s3d0 boundary-test implementation by
applying asserted source transformations. It changes the seed from r+1 to
d+1, enables FireFly, disables the ordinary Fermat solve stages, and writes all
generated artifacts to a dedicated FireFly alt_dir so prior runs cannot
contaminate the audit.
"""
from __future__ import annotations

from pathlib import Path

_SOURCE = Path(__file__).with_name("three_loop_q01_kira_exact944_r10s3d0_boundary_test.py")
if not _SOURCE.exists():
    raise SystemExit(f"ERROR: reference r10s3d0 helper not found: {_SOURCE}")

text = _SOURCE.read_text(encoding="utf-8")

# More-specific replacements must precede generic artifact-name replacements.
# Every replacement is asserted so changes to the validated reference helper
# cannot silently alter the meaning of this FireFly boundary test.
replacements = [
    (
        "It uses ordinary Kira triangular reduction + back substitution with Fermat;\nFireFly is deliberately disabled.",
        "It uses Kira finite-field reduction with FireFly enabled.\nThe FireFly artifacts are isolated from the ordinary Fermat boundary run.",
    ),
    ("R_BOUND, S_BOUND, D_BOUND = 10, 3, 0", "R_BOUND, S_BOUND, D_BOUND = 9, 3, 1"),
    ("r=10,s=3,d=0", "r=9,s=3,d=1"),
    ("planned r10s3d0 seed bounds", "planned r9s3d1 FireFly seed bounds"),
    ("basis_stable_under_r_plus_1", "basis_stable_under_d_plus_1"),
    ("basis stable under r+1", "basis stable under d+1"),
    ("after enlarging r from 9 to 10", "after enlarging d from 0 to 1"),
    ("first Q01 exact944 seed-boundary extension", "Q01 exact944 d+1 FireFly seed-boundary extension"),
    ("first one-axis stability test beyond the saved r=9,s=3,d=0 scope", "d-axis FireFly stability test beyond the saved r=9,s=3,d=0 scope"),
    ("run_triangular: true", "run_triangular: false"),
    ("run_back_substitution: true", "run_back_substitution: false"),
    ("run_firefly: false", "run_firefly: true"),
    (
        "mode: ordinary triangular + back substitution; FireFly disabled",
        "mode: FireFly finite-field reduction; ordinary solve stages disabled",
    ),
    (
        '"fresh Q01 exact944 r10s3d0 Kira/Fermat seed-boundary test"',
        '"fresh Q01 exact944 r9s3d1 Kira/FireFly seed-boundary test"',
    ),
    ("exact944_r10s3d0_fermat", "exact944_r9s3d1_firefly"),
    ("q01_exact944_r10s3d0_boundary_targets", "q01_exact944_r9s3d1_firefly_boundary_targets"),
    ("jobs_q01_exact944_r10s3d0_boundary.yaml", "jobs_q01_exact944_r9s3d1_firefly_boundary.yaml"),
    ("q01_exact944_r10s3d0_boundary.log", "q01_exact944_r9s3d1_firefly_boundary.log"),
    ("q01_exact944_r10s3d0_boundary_audit.json", "q01_exact944_r9s3d1_firefly_boundary_audit.json"),
    ("q01_exact944_r10s3d0_boundary_audit.txt", "q01_exact944_r9s3d1_firefly_boundary_audit.txt"),
    ("r10s3d0", "r9s3d1 FireFly"),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(
            "ERROR: expected reference text not found while preparing d+1 FireFly helper: "
            f"{old!r}"
        )
    text = text.replace(old, new)

# Execute the transformed, otherwise identical helper as this module.
code = compile(text, str(_SOURCE), "exec")
exec(code, globals(), globals())
