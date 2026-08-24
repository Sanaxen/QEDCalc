"""Phase-81 release validation using only the Python standard library.

This validates the packaged, already-generated Phase-81 checkpoint and the
reduction-data invariants. It intentionally does not import qedcalc, sympy, or
mpmath so that a fresh Windows Python can verify the release ZIP before the
optional scientific environment is installed.
"""
from __future__ import annotations

import csv
import math
import re
from decimal import Decimal, getcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    raise AssertionError(msg)


def version_from_pyproject() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    if not m:
        fail("version not found in pyproject.toml")
    return m.group(1)


def version_from_init() -> str:
    text = (ROOT / "qedcalc" / "__init__.py").read_text(encoding="utf-8")
    m = re.search(r'__version__\s*=\s*"([^"]+)"', text)
    if not m:
        fail("__version__ not found")
    return m.group(1)


version = version_from_pyproject()
if version != "0.88.2" or version_from_init() != version:
    fail(f"version mismatch: {version!r}")

spin_path = ROOT / "data" / "ladder_corrected_spin_sum_72_coefficients.csv"
with spin_path.open(newline="", encoding="utf-8") as f:
    spin_rows = list(csv.DictReader(f))
if len(spin_rows) != 72:
    fail(f"expected 72 projector rows, got {len(spin_rows)}")

red_path = ROOT / "data" / "ladder_corrected_40target_12basis_symbolic_reduction.csv"
with red_path.open(newline="", encoding="utf-8") as f:
    red_rows = list(csv.DictReader(f))

targets = {row["target"] for row in red_rows}
bases = {row["basis"] for row in red_rows}
if len(targets) != 40:
    fail(f"expected 40 canonical targets, got {len(targets)}")
if len(bases) != 12:
    fail(f"expected 12 terminal bases, got {len(bases)}")
if not red_rows or any(row.get("validation") != "exact" for row in red_rows):
    fail("reduction table contains a non-exact validation row")
if any(row.get("grid_validation_points") != "91" for row in red_rows):
    fail("unexpected grid_validation_points value")
if any(row.get("independent_probe_points") != "3" for row in red_rows):
    fail("unexpected independent_probe_points value")

checkpoint_path = ROOT / "output" / "phase81_ordinary_ladder_end_to_end_checkpoint.md"
checkpoint = checkpoint_path.read_text(encoding="utf-8")
required = [
    "corrected spin-sum projector table: 72 terms",
    "canonical IBP targets after symmetry combination: 40",
    "terminal analytic basis size: 12",
    "leading magnetic-projector z-pole residual: `0`",
    "Pole coefficient: `-3/4`",
    "Finite subtraction: `2`",
    "Symbolic renormalized residual: `0`",
]
for item in required:
    if item not in checkpoint:
        fail(f"checkpoint invariant missing: {item}")

bare_m = re.search(r"Numerically reconstructed `C_bare`: \*\*([^*]+)\*\*", checkpoint)
ren_m = re.search(r"Numerical end-to-end reconstruction: \*\*([^*]+)\*\*", checkpoint)
if not bare_m or not ren_m:
    fail("numeric checkpoint values not found")

getcontext().prec = 70
bare = Decimal(bare_m.group(1).strip())
ren = Decimal(ren_m.group(1).strip())
if abs((bare - ren) - Decimal(2)) > Decimal("1e-45"):
    fail(f"bare-renormalized subtraction differs from 2 beyond display-rounding tolerance: {bare-ren}")

analytic_float = 11.0 / 48.0 + math.pi * math.pi / 18.0
if abs(float(ren) - analytic_float) > 2e-15:
    fail("renormalized numeric checkpoint disagrees with analytic formula")

print("Phase-81 standard-library release audit PASS")
print("projector rows =", len(spin_rows))
print("canonical targets =", len(targets))
print("terminal bases =", len(bases))
print("bare - renormalized =", bare - ren)
print("QEDCalc", version)
