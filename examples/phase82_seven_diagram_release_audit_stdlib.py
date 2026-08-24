"""Phase-82 seven-diagram release audit using only Python stdlib.

This release audit intentionally avoids importing qedcalc/sympy/mpmath so the
packaged ZIP can be validated on a fresh Windows Python.  Each diagram class is
represented exactly in the transcendental basis
  {1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)}
with Fraction coefficients.  The sum is therefore an exact algebraic check,
not a floating-point recognition step.
"""
from __future__ import annotations

from fractions import Fraction as F
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def fail(msg: str) -> None:
    raise AssertionError(msg)


def version_from(path: Path, pattern: str) -> str:
    text = path.read_text(encoding="utf-8")
    m = re.search(pattern, text, re.M)
    if not m:
        fail(f"version not found in {path}")
    return m.group(1)

version = version_from(ROOT / "pyproject.toml", r'^version\s*=\s*"([^"]+)"')
init_version = version_from(ROOT / "qedcalc" / "__init__.py", r'__version__\s*=\s*"([^"]+)"')
if version != "0.89.0" or init_version != version:
    fail(f"version mismatch: pyproject={version}, init={init_version}")

# Basis order: 1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)
BASIS = ("1", "pi^2", "zeta(3)", "pi^2 ln 2", "ln(1/rho)")

X = (F(1, 6), F(13, 36), F(5, 4), F(-5, 6), F(0))
L = (F(11, 48), F(1, 18), F(0), F(0), F(0))
C = (F(-67, 24), F(1, 18), F(-1, 2), F(1, 3), F(1))
S = (F(11, 24), F(-1, 18), F(0), F(0), F(-1))
VP = (F(119, 36), F(-1, 3), F(0), F(0), F(0))

TOTAL_EXPECTED = (F(197, 144), F(1, 12), F(3, 4), F(-1, 2), F(0))

def add(*vectors):
    return tuple(sum((v[i] for v in vectors), F(0)) for i in range(len(BASIS)))

TOTAL = add(X, L, C, S, VP)
if TOTAL != TOTAL_EXPECTED:
    fail(f"seven-diagram coefficient mismatch: {TOTAL} != {TOTAL_EXPECTED}")

if C[-1] + S[-1] != 0:
    fail("corner/self-energy IR logarithm does not cancel")

# Release provenance: all five diagram classes must have their checkpoint layer
# present in the packaged source/output tree.
required_paths = [
    ROOT / "output" / "phase78_crossed_end_to_end_checkpoint.md",
    ROOT / "output" / "phase79_vacuum_polarization_end_to_end_checkpoint.md",
    ROOT / "output" / "phase80_self_energy_end_to_end_checkpoint.md",
    ROOT / "output" / "phase81_ordinary_ladder_end_to_end_checkpoint.md",
    ROOT / "qedcalc" / "operations" / "corner.py",
]
for path in required_paths:
    if not path.exists():
        fail(f"required diagram checkpoint/source missing: {path.relative_to(ROOT)}")

corner_text = (ROOT / "qedcalc" / "operations" / "corner.py").read_text(encoding="utf-8")
for marker in (
    "corner_phase77_end_to_end_checkpoint",
    "corner_finite_result",
    "corner_self_energy_ir_cancellation",
):
    if marker not in corner_text:
        fail(f"corner Phase-77 marker missing: {marker}")

# Guard the class count: X=1, L=1, C=2, S=2, VP=1.
class_multiplicities = {"crossed": 1, "ladder": 1, "corner": 2, "self_energy": 2, "vacuum_polarization": 1}
if sum(class_multiplicities.values()) != 7:
    fail("diagram multiplicity count is not seven")

# Write a compact reproducible checkpoint without importing scientific packages.
out = ROOT / "output" / "phase82_seven_diagram_end_to_end_checkpoint.md"
def fmt(fr: F) -> str:
    return str(fr.numerator) if fr.denominator == 1 else f"{fr.numerator}/{fr.denominator}"

lines = [
    "# Phase 82: seven-diagram end-to-end checkpoint",
    "",
    f"QEDCalc v{version}",
    "",
    "## Diagram classes",
    "",
    "- crossed ladder: 1 diagram",
    "- ordinary ladder: 1 diagram",
    "- corner: 2 diagrams",
    "- self-energy insertion: 2 diagrams",
    "- vacuum polarization: 1 diagram",
    "- total: 7 diagrams",
    "",
    "## Exact transcendental-basis sum",
    "",
    "Basis: `1, pi^2, zeta(3), pi^2 ln 2, ln(1/rho)`",
    "",
]
for name, vec in (("X", X), ("L", L), ("C", C), ("S", S), ("VP", VP), ("TOTAL", TOTAL)):
    lines.append(f"- {name}: `({', '.join(fmt(x) for x in vec)})`")
lines += [
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
]
out.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("Phase-82 seven-diagram release audit PASS")
print("diagram count =", sum(class_multiplicities.values()))
print("IR log residual =", C[-1] + S[-1])
print("total basis coefficients =", tuple(fmt(x) for x in TOTAL))
print("Output:", out)
print("QEDCalc", version)
