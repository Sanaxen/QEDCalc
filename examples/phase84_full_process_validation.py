"""Validate Phase 84 full two-loop process-report generation using stdlib only."""
from __future__ import annotations

import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

runpy.run_path(str(ROOT / "examples" / "phase84_two_loop_full_process_report.py"), run_name="__main__")


def validate_math_layout(name: str, text: str) -> None:
    parts = text.split("$$")
    for i in range(1, len(parts), 2):
        block = parts[i]
        lines = [line.rstrip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        structured = any("\\begin{" in line for line in lines)
        if not structured:
            longest = max(len(line) for line in lines)
            if longest > 120:
                raise AssertionError(f"{name}: long unwrapped display line ({longest} chars)")
            # A short standalone expression is allowed to begin with a unary
            # minus. The no-operator-at-line-start rule concerns continuation
            # lines created by wrapping.
            continue

        # For aligned displays, verify continuation rows after the first
        # mathematical row. Environment declarations are skipped.
        math_rows = []
        in_aligned = False
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(r"\begin{aligned"):
                in_aligned = True
                continue
            if stripped.startswith(r"\end{aligned"):
                in_aligned = False
                continue
            if in_aligned:
                if stripped.startswith("&"):
                    stripped = stripped[1:].lstrip()
                math_rows.append(stripped)
        for row in math_rows[1:]:
            if row.startswith(("=", "+", "-", r"\times", r"\cdot")):
                raise AssertionError(f"{name}: wrapped continuation begins with operator: {row!r}")


expected = {
    "2loop_crossed_ladder_full.md": ("Crossed ladder", "crossed_ladder_2loop_bare.tex"),
    "2loop_ordinary_ladder_full.md": ("Ordinary ladder", "ordinary_ladder_2loop_bare.tex"),
    "2loop_corner_full.md": ("Corner pair", "corner_4_2loop_bare_feynman_gauge.tex"),
    "2loop_self_energy_full.md": ("Self-energy insertion pair", "self_energy_insertion_left_2loop_bare.tex"),
    "2loop_vacuum_polarization_full.md": ("Vacuum polarization", "vacuum_polarization_2loop_bare.tex"),
}

for name, tokens in expected.items():
    path = ROOT / "output" / name
    if not path.exists():
        raise AssertionError(f"missing generated report: {name}")
    text = path.read_text(encoding="utf-8")
    required = (
        "## 1. Raw input expressions",
        "## 2. Complete calculation-process guide",
        "## 3. Recorded runtime artifacts",
        "Long display equations are wrapped automatically",
        *tokens,
    )
    for token in required:
        if token not in text:
            raise AssertionError(f"{name}: missing token {token!r}")
    validate_math_layout(name, text)

master = ROOT / "output" / "2loop_all_7diagrams_full.md"
if not master.exists():
    raise AssertionError("missing generated master report")
master_text = master.read_text(encoding="utf-8")
for token in (
    "1 + 1 + 2 + 2 + 1 = 7",
    "2loop_crossed_ladder_full.md",
    "2loop_ordinary_ladder_full.md",
    "2loop_corner_full.md",
    "2loop_self_energy_full.md",
    "2loop_vacuum_polarization_full.md",
    "Exact seven-diagram assembly",
    "Complete two-loop regression",
):
    if token not in master_text:
        raise AssertionError(f"master report missing token {token!r}")
validate_math_layout(master.name, master_text)

print("Phase-84 full two-loop process report validation PASS")
print("generated reports = 6")
print("math layout validation = PASS")
print("master =", master)
