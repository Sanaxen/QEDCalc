"""Phase 84: build complete two-loop process Markdown reports.

This reporting layer does not change physics. It combines raw LaTeX input,
the detailed process manuals, recorded output Markdown, large algebra-table
inventories, and the seven-diagram regression into complete process reports.
It also applies presentation-only line wrapping to long display equations so
that GitHub/Markdown rendering does not clip them horizontally.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from qedcalc.reporting import format_markdown_math

INPUT = ROOT / "input"
OUTPUT = ROOT / "output"
DOC = ROOT / "doc" / "QEDCalc_2loop_5sample_manuals_v2"

@dataclass(frozen=True)
class GraphSpec:
    slug: str
    title: str
    multiplicity: int
    inputs: tuple[str, ...]
    manual: str
    md_patterns: tuple[str, ...]
    data_patterns: tuple[str, ...]
    release_phase: int

SPECS = (
    GraphSpec("crossed_ladder", "Crossed ladder", 1,
              ("crossed_ladder_2loop_bare.tex",),
              "01_crossed_ladder_QEDCalcサンプル説明書兼計算過程説明書.md",
              ("crossed*.md", "phase*crossed*.md", "phase78*.md"),
              ("crossed*.csv", "crossed*.txt"), 78),
    GraphSpec("ordinary_ladder", "Ordinary ladder", 1,
              ("ordinary_ladder_2loop_bare.tex",),
              "02_ordinary_ladder_QEDCalcサンプル説明書兼計算過程説明書.md",
              ("ladder*.md", "phase*ladder*.md", "phase81*.md"),
              ("ladder*.csv", "ladder*.txt"), 81),
    GraphSpec("corner", "Corner pair", 2,
              ("corner_4_2loop_bare_feynman_gauge.tex", "corner_5_2loop_bare_feynman_gauge.tex"),
              "03_corner_2図_QEDCalcサンプル説明書兼計算過程説明書.md",
              ("corner*.md", "phase*corner*.md", "phase77*.md"),
              ("corner*.csv", "corner*.txt"), 77),
    GraphSpec("self_energy", "Self-energy insertion pair", 2,
              ("self_energy_insertion_left_2loop_bare.tex", "self_energy_insertion_right_2loop_bare.tex", "self_energy_subloop_numerator.tex"),
              "04_self_energy_insertion_2図_QEDCalcサンプル説明書兼計算過程説明書.md",
              ("self_energy*.md", "phase*self_energy*.md", "phase80*.md"),
              ("self_energy*.csv", "self_energy*.txt"), 80),
    GraphSpec("vacuum_polarization", "Vacuum polarization", 1,
              ("vacuum_polarization_2loop_bare.tex", "vacuum_polarization_subloop.tex"),
              "05_vacuum_polarization_QEDCalcサンプル説明書兼計算過程説明書.md",
              ("vacuum_polarization*.md", "phase*vacuum*.md", "phase79*.md"),
              ("vacuum_polarization*.csv", "vacuum_polarization*.txt"), 79),
)


def require(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"required file missing: {path.relative_to(ROOT)}")


def text(path: Path) -> str:
    require(path)
    return path.read_text(encoding="utf-8")


def phase_key(path: Path):
    m = re.search(r"phase(\d+)", path.name, re.I)
    return (int(m.group(1)) if m else -1, path.name.lower())


def collect(patterns, suffixes):
    found = {}
    for pattern in patterns:
        for path in OUTPUT.glob(pattern):
            if path.name.startswith("2loop_") or path.suffix.lower() not in suffixes:
                continue
            found[path.name] = path
    return sorted(found.values(), key=phase_key)


def demote(md: str) -> str:
    out = []
    fence = False
    for line in md.splitlines():
        if line.startswith("```"):
            fence = not fence
            out.append(line)
        elif not fence and line.startswith("#"):
            out.append("##" + line)
        else:
            out.append(line)
    return "\n".join(out).strip()


def readable(md: str) -> str:
    """Apply presentation-only display-math wrapping after heading adjustment."""
    return format_markdown_math(md, max_width=92)


def nlines(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def graph_report(spec: GraphSpec):
    md_files = collect(spec.md_patterns, (".md",))
    data_files = collect(spec.data_patterns, (".csv", ".txt"))
    manual = DOC / spec.manual
    require(manual)

    lines = [
        f"# QEDCalc two-loop full process report: {spec.title}", "",
        f"Diagram multiplicity: **{spec.multiplicity}**.", "",
        "This report records raw input, the human/QEDCalc handoff, actual output artifacts, large algebra tables, and release status.", "",
        "Long display equations are wrapped automatically for readability. The mathematical content is unchanged, and continuation lines never begin with `=`, `+`, `-`, `\\times`, or `\\cdot`.", "",
        "## 1. Raw input expressions", "",
    ]
    for name in spec.inputs:
        p = INPUT / name
        require(p)
        raw_block = "$$\n" + text(p).strip() + "\n$$"
        lines += [f"### `input/{name}`", "", readable(raw_block), ""]

    lines += [
        "## 2. Complete calculation-process guide", "",
        f"Source: `doc/QEDCalc_2loop_5sample_manuals_v2/{spec.manual}`", "",
        "This embedded guide states what a person derives, what is passed to QEDCalc, which program section performs the algebra, what QEDCalc returns, and how that output becomes the next input.", "",
        readable(demote(text(manual))), "",
        "## 3. Recorded runtime artifacts", "",
        "| Artifact | Type | Lines | Bytes |", "| --- | --- | ---: | ---: |",
    ]
    for p in md_files + data_files:
        lines.append(f"| `output/{p.name}` | `{p.suffix[1:]}` | {nlines(p)} | {p.stat().st_size} |")

    lines += ["", "## 4. Recorded Markdown stages", ""]
    if md_files:
        for i, p in enumerate(md_files, 1):
            lines += [f"### 4.{i} `output/{p.name}`", "", readable(demote(text(p))), "", "---", ""]
    else:
        lines += ["No graph-specific runtime Markdown is currently stored.", ""]

    lines += ["## 5. Large algebra/reduction files", ""]
    if data_files:
        for p in data_files:
            lines.append(f"- `output/{p.name}` — {nlines(p)} lines, {p.stat().st_size} bytes")
    else:
        lines.append("No graph-specific CSV/TXT artifact is currently stored.")

    release = [p for p in md_files if f"phase{spec.release_phase}" in p.name.lower()]
    lines += ["", "## 6. Release-layer status", ""]
    if release:
        lines.append(f"Phase {spec.release_phase} artifact(s): " + ", ".join(f"`output/{p.name}`" for p in release) + ".")
    else:
        lines.append(f"No Phase {spec.release_phase} Markdown artifact is currently stored; rerun that scientific phase when a freshly regenerated checkpoint is required.")
    lines += ["", "The reporter never fabricates a missing scientific artifact; documented stages and files actually present on disk remain explicitly distinguishable.", ""]

    content = readable("\n".join(lines).rstrip() + "\n")
    out = OUTPUT / f"2loop_{spec.slug}_full.md"
    out.write_text(content, encoding="utf-8")
    return out, content


def master_report(reports):
    p82 = OUTPUT / "phase82_seven_diagram_end_to_end_checkpoint.md"
    p83 = OUTPUT / "phase83_two_loop_completion_regression.md"
    require(p82); require(p83)
    lines = [
        "# QEDCalc complete two-loop calculation record — all seven diagrams", "",
        "The five graph-class reports below represent 1 + 1 + 2 + 2 + 1 = 7 diagrams.", "",
        "Long display equations are wrapped automatically for readable GitHub/Markdown rendering.", "",
        "## 1. Report index", "",
        "| Class | Multiplicity | Report |", "| --- | ---: | --- |",
    ]
    for spec, path, _ in reports:
        lines.append(f"| {spec.title} | {spec.multiplicity} | `output/{path.name}` |")
    lines += ["", "## 2. Full graph-class records", ""]
    for i, (spec, path, content) in enumerate(reports, 1):
        lines += [f"### 2.{i} {spec.title}", "", f"Source: `output/{path.name}`", "", demote(content), "", "---", ""]
    lines += ["## 3. Exact seven-diagram assembly", "", demote(text(p82)), "", "---", "", "## 4. Complete two-loop regression", "", demote(text(p83)), ""]
    out = OUTPUT / "2loop_all_7diagrams_full.md"
    out.write_text(readable("\n".join(lines).rstrip() + "\n"), encoding="utf-8")
    return out


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    reports = []
    for spec in SPECS:
        path, content = graph_report(spec)
        reports.append((spec, path, content))
        print("generated:", path.relative_to(ROOT))
    master = master_report(reports)
    print("generated:", master.relative_to(ROOT))
    print("Phase-84 full two-loop process reporting PASS")

if __name__ == "__main__":
    main()
