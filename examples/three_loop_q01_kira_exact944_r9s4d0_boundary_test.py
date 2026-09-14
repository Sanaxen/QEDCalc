"""Run/audit the Q01 exact944 s+1 seed-boundary extension: r=9,s=4,d=0.

This helper deliberately reuses the already validated r10s3d0 boundary-test
implementation by applying a small, asserted source transformation. That keeps
all target construction and audit logic identical while changing only the seed
bounds, artifact names, and scientific label from r+1 to s+1.
"""
from __future__ import annotations

from pathlib import Path

_SOURCE = Path(__file__).with_name("three_loop_q01_kira_exact944_r10s3d0_boundary_test.py")
if not _SOURCE.exists():
    raise SystemExit(f"ERROR: reference r10s3d0 helper not found: {_SOURCE}")

text = _SOURCE.read_text(encoding="utf-8")

# Keep these replacements asserted so a future edit of the validated r+1 helper
# cannot silently change the meaning of this s+1 test. More-specific phrases
# must be replaced before the generic r10s3d0 artifact-name replacement.
replacements = [
    ("R_BOUND, S_BOUND, D_BOUND = 10, 3, 0", "R_BOUND, S_BOUND, D_BOUND = 9, 4, 0"),
    ("r=10,s=3,d=0", "r=9,s=4,d=0"),
    ("planned r10s3d0 seed bounds", "planned r9s4d0 seed bounds"),
    ("basis_stable_under_r_plus_1", "basis_stable_under_s_plus_1"),
    ("basis stable under r+1", "basis stable under s+1"),
    ("after enlarging r from 9 to 10", "after enlarging s from 3 to 4"),
    ("first Q01 exact944 seed-boundary extension", "Q01 exact944 s+1 seed-boundary extension"),
    ("first one-axis stability test beyond the saved r=9,s=3,d=0 scope", "s-axis stability test beyond the saved r=9,s=3,d=0 scope"),
    ("r10s3d0", "r9s4d0"),
]

for old, new in replacements:
    if old not in text:
        raise SystemExit(f"ERROR: expected reference text not found while preparing s+1 helper: {old!r}")
    text = text.replace(old, new)

# Execute the transformed, otherwise identical helper as this module.
code = compile(text, str(_SOURCE), "exec")
exec(code, globals(), globals())
