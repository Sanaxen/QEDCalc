"""Validate Phase 84 full two-loop process-report generation using stdlib only."""
from __future__ import annotations

import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

runpy.run_path(str(ROOT / "examples" / "phase84_two_loop_full_process_report.py"), run_name="__main__")


def display_width(source: str) -> int:
    text = re.sub(r"\\[A-Za-z]+", "X", source)
    text = text.replace("{", "").replace("}", "")
    return len(text)


def balanced_braces(source: str) -> bool:
    depth = 0
    i = 0
    while i < len(source):
        if source[i] == "\\" and i + 1 < len(source) and source[i + 1] in "{}":
            i += 2
            continue
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth < 0:
                return False
        i += 1
    return depth == 0


def balanced_left_right(source: str) -> bool:
    """Require every display block to contain complete nested \\left/\\right pairs."""
    stack: list[str] = []
    pairs = {"(": ")", "[": "]", r"\{": r"\}"}
    i = 0
    while i < len(source):
        if source.startswith(r"\left", i):
            j = i + len(r"\left")
            if source.startswith(r"\{", j):
                opening = r"\{"
                j += 2
            elif j < len(source) and source[j] in "([":
                opening = source[j]
                j += 1
            else:
                i += len(r"\left")
                continue
            stack.append(pairs[opening])
            i = j
            continue
        if source.startswith(r"\right", i):
            j = i + len(r"\right")
            if source.startswith(r"\}", j):
                closing = r"\}"
                j += 2
            elif j < len(source) and source[j] in ")]":
                closing = source[j]
                j += 1
            else:
                return False
            if not stack or stack[-1] != closing:
                return False
            stack.pop()
            i = j
            continue
        i += 1
    return not stack


def validate_math_layout(name: str, text: str) -> None:
    parts = text.split("$$")
    if len(parts) % 2 == 0:
        raise AssertionError(f"{name}: unmatched $$ display delimiters")

    proxy_defs = 0
    for i in range(1, len(parts), 2):
        block = parts[i].strip()
        if not block:
            continue

        if not balanced_braces(block):
            raise AssertionError(f"{name}: unbalanced TeX braces in display block")
        if not balanced_left_right(block):
            raise AssertionError(
                f"{name}: unbalanced \\left/\\right delimiters in display block: {block[:120]!r}"
            )

        if r"\frac{" in block and r"\begin{aligned}" in block:
            raise AssertionError(
                f"{name}: aligned environment embedded in a fraction display"
            )

        if re.match(r"^[DNE]_\{[0-9,]+\}\s*=", block):
            proxy_defs += 1

        structured = any(
            marker in block
            for marker in (
                r"\begin{aligned}", r"\begin{alignedat}", r"\begin{split}",
                r"\begin{cases}", r"\begin{array}", r"\begin{matrix}",
                r"\begin{pmatrix}", r"\begin{bmatrix}", r"\begin{gathered}",
                r"\begin{multline}",
            )
        )

        if structured:
            if r"\begin{aligned}" in block:
                rows = []
                inside = False
                for line in block.splitlines():
                    s = line.strip()
                    if s.startswith(r"\begin{aligned}"):
                        inside = True
                        continue
                    if s.startswith(r"\end{aligned}"):
                        inside = False
                        continue
                    if inside:
                        if s.startswith("&"):
                            s = s[1:].lstrip()
                        if s.endswith(r"\\"):
                            s = s[:-2].rstrip()
                        if s:
                            rows.append(s)
                for row_no, row in enumerate(rows, 1):
                    if row_no > 1 and row.startswith(("=", "+", "-", r"\times", r"\cdot")):
                        raise AssertionError(
                            f"{name}: aligned continuation begins with operator: {row!r}"
                        )
            continue

        width = display_width(block)
        if width > 110:
            raise AssertionError(
                f"{name}: long unsplit display remains "
                f"(estimated width {width}, raw chars {len(block)}): {block[:120]!r}"
            )

    return proxy_defs


expected = {
    "2loop_crossed_ladder_full.md": ("Crossed ladder", "crossed_ladder_2loop_bare.tex"),
    "2loop_ordinary_ladder_full.md": ("Ordinary ladder", "ordinary_ladder_2loop_bare.tex"),
    "2loop_corner_full.md": ("Corner pair", "corner_4_2loop_bare_feynman_gauge.tex"),
    "2loop_self_energy_full.md": ("Self-energy insertion pair", "self_energy_insertion_left_2loop_bare.tex"),
    "2loop_vacuum_polarization_full.md": ("Vacuum polarization", "vacuum_polarization_2loop_bare.tex"),
}

proxy_total = 0
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
    proxy_total += validate_math_layout(name, text)

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
proxy_total += validate_math_layout(master.name, master_text)

print("Phase-84 full two-loop process report validation PASS")
print("generated reports = 6")
print("math layout validation = PASS")
print("recursive proxy definitions =", proxy_total)
print("master =", master)
