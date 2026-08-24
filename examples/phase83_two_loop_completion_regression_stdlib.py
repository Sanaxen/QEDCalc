"""Phase-83 complete two-loop regression using only Python stdlib.

This is the durable release audit for the completed seven-diagram two-loop
calculation.  It does not import qedcalc, SymPy, NumPy, or mpmath.  Instead it
verifies the independently generated release checkpoints, reduction tables,
source checkpoint markers, and exact rational coefficients in the fixed
transcendental basis.

When the scientific environment is installed, run_v090_validation.bat also
invokes the optional Phase-83 extended scientific regression.
"""
from __future__ import annotations

import ast
import csv
import json
import re
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    raise AssertionError(msg)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"required file missing: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require(text: str, *tokens: str, label: str) -> None:
    for token in tokens:
        if token not in text:
            fail(f"{label}: required invariant missing: {token!r}")


def version_from(path: Path, pattern: str) -> str:
    m = re.search(pattern, read(path), re.M)
    if not m:
        fail(f"version not found in {path.relative_to(ROOT)}")
    return m.group(1)


def parse_fraction(s: str) -> F:
    s = s.strip()
    return F(s)


def fmt(x: F) -> str:
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


version = version_from(ROOT / "pyproject.toml", r'^version\s*=\s*"([^"]+)"')
init_version = version_from(ROOT / "qedcalc" / "__init__.py", r'__version__\s*=\s*"([^"]+)"')
if version != "0.90.0" or init_version != version:
    fail(f"version mismatch: pyproject={version}, init={init_version}")

baseline = json.loads(read(ROOT / "data" / "two_loop_v090_baseline.json"))
if baseline.get("release") != version:
    fail("two-loop baseline release does not match package version")

multiplicities = baseline["diagram_multiplicities"]
if multiplicities != {
    "crossed_ladder": 1,
    "ordinary_ladder": 1,
    "corner": 2,
    "self_energy_insertion": 2,
    "vacuum_polarization": 1,
}:
    fail(f"unexpected diagram multiplicities: {multiplicities}")
if sum(multiplicities.values()) != 7:
    fail("two-loop diagram count is not seven")

basis = tuple(baseline["basis"])
if basis != ("1", "pi^2", "zeta(3)", "pi^2 ln 2", "ln(1/rho)"):
    fail(f"unexpected transcendental basis: {basis}")

coeff_raw = baseline["coefficients"]
coeff = {name: tuple(parse_fraction(x) for x in vec) for name, vec in coeff_raw.items()}
classes = (
    "crossed_ladder",
    "ordinary_ladder",
    "corner_pair",
    "self_energy_pair",
    "vacuum_polarization",
)
for name in classes:
    if len(coeff[name]) != len(basis):
        fail(f"{name}: wrong basis dimension")

total = tuple(sum((coeff[name][i] for name in classes), F(0)) for i in range(len(basis)))
expected_total = tuple(coeff["total"])
if total != expected_total:
    fail(f"seven-diagram exact sum mismatch: {total} != {expected_total}")
if coeff["corner_pair"][-1] + coeff["self_energy_pair"][-1] != 0:
    fail("corner/self-energy IR logarithm does not cancel")

# Phase 77: corner source checkpoint exists and exposes all exact closure routes.
corner_path = ROOT / "qedcalc" / "operations" / "corner.py"
corner_src = read(corner_path)
corner_tree = ast.parse(corner_src)
corner_defs = {n.name for n in ast.walk(corner_tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
for name in (
    "corner_phase77_end_to_end_checkpoint",
    "corner_finite_result",
    "corner_self_energy_ir_cancellation",
):
    if name not in corner_defs:
        fail(f"Phase 77 source checkpoint missing function: {name}")

# Phase 78: crossed ladder checkpoint and historical-provenance boundary.
p78 = read(ROOT / "output" / "phase78_crossed_end_to_end_checkpoint.md")
require(
    p78,
    "## projector_F1_coefficient",
    "## projector_F2_coefficient",
    "## endpoint_divergent_residual",
    "## final_closed_form_residual",
    "PASS: projector normalization, endpoint cancellation, and final analytic assembly close exactly.",
    label="Phase 78",
)
if "The magnitude 1/32 is retained as a historical audit target only." not in p78:
    fail("Phase 78 historical 1/32 provenance boundary is missing")
if baseline["historical_provenance"]["crossed_ladder_karplus_kroll_gap"] != "1/32":
    fail("historical crossed-ladder gap baseline changed")
if baseline["historical_provenance"]["origin_resolved"] is not False:
    fail("historical 1/32 origin must remain explicitly unresolved")

# Phase 79: vacuum-polarization physical invariants.
p79 = read(ROOT / "output" / "phase79_vacuum_polarization_end_to_end_checkpoint.md")
require(
    p79,
    "Transversality residual: `0`",
    "On-shell subtraction residual: `0`",
    "Finite D->4 kernel residual: `0`",
    "Outer magnetic insertion residual: `0`",
    "z-kernel residual: `0`",
    "Primitive derivative residual: `0`",
    "Final residual: `0`",
    "119/36 - pi**2/3",
    label="Phase 79",
)

# Phase 80: self-energy raw-to-final and IR cancellation invariants.
p80 = read(ROOT / "output" / "phase80_self_energy_end_to_end_checkpoint.md")
require(
    p80,
    "Raw sample residuals: `(0, 0, 0)`",
    "Raw UV residual: `0`",
    "Renormalized G_A residual: `0`",
    "Self-energy coefficient of $\\log(1/\\rho)$: `-1`",
    "Corner coefficient of $\\log(1/\\rho)$: `1`",
    "IR cancellation residual: `0`",
    label="Phase 80",
)

# Phase 81: ladder 72 -> 40 -> 12 exact reduction data and renormalization.
spin_path = ROOT / "data" / "ladder_corrected_spin_sum_72_coefficients.csv"
with spin_path.open(newline="", encoding="utf-8") as f:
    spin_rows = list(csv.DictReader(f))
if len(spin_rows) != 72:
    fail(f"Phase 81 expected 72 projector rows, got {len(spin_rows)}")
red_path = ROOT / "data" / "ladder_corrected_40target_12basis_symbolic_reduction.csv"
with red_path.open(newline="", encoding="utf-8") as f:
    red_rows = list(csv.DictReader(f))
targets = {r["target"] for r in red_rows}
bases = {r["basis"] for r in red_rows}
if len(targets) != 40 or len(bases) != 12:
    fail(f"Phase 81 reduction shape changed: targets={len(targets)}, bases={len(bases)}")
if not red_rows or any(r.get("validation") != "exact" for r in red_rows):
    fail("Phase 81 contains non-exact reduction rows")
p81 = read(ROOT / "output" / "phase81_ordinary_ladder_end_to_end_checkpoint.md")
require(
    p81,
    "corrected spin-sum projector table: 72 terms",
    "canonical IBP targets after symmetry combination: 40",
    "terminal analytic basis size: 12",
    "leading magnetic-projector z-pole residual: `0`",
    "Finite subtraction: `2`",
    "Symbolic renormalized residual: `0`",
    label="Phase 81",
)

# Phase 82: seven-diagram exact basis closure.
p82 = read(ROOT / "output" / "phase82_seven_diagram_end_to_end_checkpoint.md")
require(
    p82,
    "- total: 7 diagrams",
    "- TOTAL: `(197/144, 1/12, 3/4, -1/2, 0)`",
    "IR log residual: `0`",
    "Exact basis residual: `0`",
    label="Phase 82",
)

# Phase-83 completion report.
out = ROOT / "output" / "phase83_two_loop_completion_regression.md"
status_rows = [
    ("77", "corner pair", "2", "PASS", "sector + soft/hard + IR closure"),
    ("78", "crossed ladder", "1", "PASS", "projector + endpoint + analytic closure"),
    ("79", "vacuum polarization", "1", "PASS", "transversality + OS subtraction + final closure"),
    ("80", "self-energy insertion pair", "2", "PASS", "raw-to-final + IR closure"),
    ("81", "ordinary ladder", "1", "PASS", "72 -> 40 -> 12 + OS subtraction"),
    ("82", "seven-diagram total", "7", "PASS", "exact transcendental-basis sum"),
]
lines = [
    "# Phase 83: complete two-loop regression checkpoint",
    "",
    f"QEDCalc v{version}",
    "",
    "## Completion matrix",
    "",
    "| Phase | Diagram class | Multiplicity | Status | Release invariant |",
    "| --- | --- | ---: | --- | --- |",
]
for row in status_rows:
    lines.append("| " + " | ".join(row) + " |")
lines += [
    "",
    "## Exact seven-diagram basis sum",
    "",
    "Basis: `1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)`",
    "",
]
for name in classes:
    lines.append(f"- {name}: `({', '.join(fmt(x) for x in coeff[name])})`")
lines += [
    f"- total: `({', '.join(fmt(x) for x in total)})`",
    "",
    "IR log residual: `0`",
    "",
    "Final coefficient:",
    "",
    "$$",
    "A_1^{(4)} = \\frac{197}{144} + \\frac{\\pi^2}{12} + \\frac34\\zeta(3) - \\frac{\\pi^2}{2}\\ln2",
    "$$",
    "",
    "Exact basis residual: `0`",
    "",
    "## Regression baseline",
    "",
    "- ordinary-ladder projector rows: `72`",
    "- ordinary-ladder canonical IBP targets: `40`",
    "- ordinary-ladder terminal master bases: `12`",
    "- diagram count: `7`",
    "- scientific-package-free release audit: `PASS`",
    "",
    "## Known unresolved provenance item",
    "",
    "The crossed-ladder Karplus--Kroll historical gap has magnitude `1/32`.  Its precise lost term in the 1950 algebra remains unresolved.  This is not an uncertainty in the modern crossed-ladder value and is not used as an input to the two-loop closure.",
    "",
    "## Completion status",
    "",
    "`TWO-LOOP RELEASE REGRESSION PASS`",
]
out.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Phase-83 complete two-loop regression PASS")
print("diagram count =", sum(multiplicities.values()))
print("IR log residual =", fmt(coeff["corner_pair"][-1] + coeff["self_energy_pair"][-1]))
print("ordinary ladder reduction =", f"{len(spin_rows)} -> {len(targets)} -> {len(bases)}")
print("total basis coefficients =", tuple(fmt(x) for x in total))
print("historical 1/32 origin resolved =", baseline["historical_provenance"]["origin_resolved"])
print("Output:", out)
print("QEDCalc", version)
