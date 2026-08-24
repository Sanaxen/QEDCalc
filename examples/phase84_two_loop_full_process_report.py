"""Phase 84: build full two-loop process Markdown reports from recorded artifacts.

This reporting layer does not change any physics calculation.  It gathers the
raw LaTeX inputs and all graph-specific Markdown/CSV/TXT artifacts already
produced by the validated QEDCalc routes, orders them into one auditable
calculation record per graph class, and finally builds a seven-diagram master
report.

The script intentionally uses only the Python standard library so that the
report can be rebuilt even on a machine where the optional scientific stack is
not currently installed.  Scientific checkpoints remain the responsibility of
their dedicated phase scripts and v0.90+ regressions.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "input"
OUTPUT = ROOT / "output"


@dataclass(frozen=True)
class GraphSpec:
    slug: str
    title: str
    multiplicity: int
    input_files: tuple[str, ...]
    md_patterns: tuple[str, ...]
    data_patterns: tuple[str, ...]
    final_checkpoint: str


SPECS = (
    GraphSpec(
        "crossed_ladder",
        "Crossed ladder",
        1,
        ("crossed_ladder_2loop_bare.tex",),
        ("crossed*.md", "phase*crossed*.md", "phase78*.md"),
        ("crossed*.csv", "crossed*.txt"),
        "phase78_crossed_end_to_end_checkpoint.md",
    ),
    GraphSpec(
        "ordinary_ladder",
        "Ordinary ladder",
        1,
        ("ordinary_ladder_2loop_bare.tex",),
        ("ladder*.md", "phase*ladder*.md", "phase81*.md"),
        ("ladder*.csv", "ladder*.txt"),
        "phase81_ordinary_ladder_end_to_end_checkpoint.md",
    ),
    GraphSpec(
        "corner",
        "Corner pair",
        2,
        (
            "corner_4_2loop_bare_feynman_gauge.tex",
            "corner_5_2loop_bare_feynman_gauge.tex",
        ),
        ("corner*.md", "phase*corner*.md", "phase77*.md"),
        ("corner*.csv", "corner*.txt"),
        "phase77_corner_end_to_end_checkpoint.md",
    ),
    GraphSpec(
        "self_energy",
        "Self-energy insertion pair",
        2,
        (
            "self_energy_insertion_left_2loop_bare.tex",
            "self_energy_insertion_right_2loop_bare.tex",
            "self_energy_subloop_numerator.tex",
        ),
        ("self_energy*.md", "phase*self_energy*.md", "phase80*.md"),
        ("self_energy*.csv", "self_energy*.txt"),
        "phase80_self_energy_end_to_end_checkpoint.md",
    ),
    GraphSpec(
        "vacuum_polarization",
        "Vacuum polarization",
        1,
        (
            "vacuum_polarization_2loop_bare.tex",
            "vacuum_polarization_subloop.tex",
        ),
        ("vacuum_polarization*.md", "phase*vacuum*.md", "phase79*.md"),
        ("vacuum_polarization*.csv", "vacuum_polarization*.txt"),
        "phase79_vacuum_polarization_end_to_end_checkpoint.md",
    ),
)

GENERATED_PREFIX = "2loop_"


def require(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"required artifact missing: {path.relative_to(ROOT)}")


def read(path: Path) -> str:
    require(path)
    return path.read_text(encoding="utf-8")


def phase_key(path: Path) -> tuple[int, str]:
    m = re.search(r"phase(\d+)", path.name, re.I)
    if m:
        return (int(m.group(1)), path.name.lower())
    # Raw/trial reports precede numbered release checkpoints.
    return (-1, path.name.lower())


def collect(patterns: tuple[str, ...], suffixes: tuple[str, ...]) -> list[Path]:
    found: dict[str, Path] = {}
    for pattern in patterns:
        for path in OUTPUT.glob(pattern):
            if path.name.startswith(GENERATED_PREFIX):
                continue
            if path.suffix.lower() not in suffixes:
                continue
            found[path.name] = path
    return sorted(found.values(), key=phase_key)


def demote_headings(text: str) -> str:
    """Keep embedded Markdown readable inside a larger generated report."""
    lines = []
    for line in text.splitlines():
        if line.startswith("#"):
            lines.append("##" + line)
        else:
            lines.append(line)
    return "\n".join(lines).strip()


def line_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        return sum(1 for _ in f)


def raw_input_section(spec: GraphSpec) -> list[str]:
    lines = ["## 1. Raw input expressions", ""]
    lines.append(
        "These are the human-supplied Feynman-rule inputs from which the "
        "recorded QEDCalc route starts."
    )
    lines.append("")
    for name in spec.input_files:
        path = INPUT / name
        require(path)
        expr = read(path).strip()
        lines += [f"### `input/{name}`", "", "$$", expr, "$$", ""]
    return lines


def artifact_inventory(md_files: list[Path], data_files: list[Path]) -> list[str]:
    lines = ["## 2. Recorded calculation artifacts", ""]
    lines += [
        "The files below are the actual recorded artifacts used to reconstruct "
        "this full process report. Markdown stages are embedded in full below; "
        "large CSV/TXT algebra tables are referenced by path, line count, and size.",
        "",
        "| Artifact | Type | Lines | Bytes |",
        "| --- | --- | ---: | ---: |",
    ]
    for path in md_files + data_files:
        lines.append(
            f"| `output/{path.name}` | `{path.suffix.lstrip('.')}` | "
            f"{line_count(path)} | {path.stat().st_size} |"
        )
    lines.append("")
    return lines


def markdown_stages(md_files: list[Path]) -> list[str]:
    lines = ["## 3. Full recorded Markdown stages", ""]
    if not md_files:
        lines += ["No graph-specific Markdown artifact was found.", ""]
        return lines
    for i, path in enumerate(md_files, 1):
        lines += [
            f"### 3.{i} Recorded artifact: `output/{path.name}`",
            "",
            demote_headings(read(path)),
            "",
            "---",
            "",
        ]
    return lines


def data_stage(data_files: list[Path]) -> list[str]:
    lines = ["## 4. Large algebra/reduction artifacts", ""]
    if not data_files:
        lines += ["No graph-specific CSV/TXT artifact was found.", ""]
        return lines
    lines.append(
        "These files are part of the full calculation record but are not expanded "
        "inline because they can contain tens to hundreds of algebraic rows."
    )
    lines.append("")
    for path in data_files:
        lines += [
            f"- `output/{path.name}` — {line_count(path)} lines, {path.stat().st_size} bytes",
        ]
    lines.append("")
    return lines


def graph_report(spec: GraphSpec) -> tuple[Path, str]:
    md_files = collect(spec.md_patterns, (".md",))
    data_files = collect(spec.data_patterns, (".csv", ".txt"))
    require(OUTPUT / spec.final_checkpoint)
    if OUTPUT / spec.final_checkpoint not in md_files:
        md_files.append(OUTPUT / spec.final_checkpoint)
        md_files = sorted(set(md_files), key=phase_key)

    lines = [
        f"# QEDCalc two-loop full process report: {spec.title}",
        "",
        f"Diagram multiplicity represented by this route: **{spec.multiplicity}**.",
        "",
        "This file is an execution-record view of the calculation. It begins with "
        "the raw LaTeX input and then embeds every graph-specific Markdown artifact "
        "currently present in `output/`, followed by an inventory of the large "
        "CSV/TXT algebra artifacts. It complements, rather than replaces, the "
        "human-readable derivation/program manuals under `doc/`.",
        "",
    ]
    lines += raw_input_section(spec)
    lines += artifact_inventory(md_files, data_files)
    lines += markdown_stages(md_files)
    lines += data_stage(data_files)
    lines += [
        "## 5. Route closure", "",
        f"Release checkpoint: `output/{spec.final_checkpoint}`", "",
        "The presence of that checkpoint in section 3 records the final validated "
        "closure for this diagram class. Earlier artifacts in the same section are "
        "the recorded intermediate route that led to the release checkpoint.",
        "",
    ]
    content = "\n".join(lines).rstrip() + "\n"
    out = OUTPUT / f"2loop_{spec.slug}_full.md"
    out.write_text(content, encoding="utf-8")
    return out, content


def build_master(reports: list[tuple[GraphSpec, Path, str]]) -> Path:
    p82 = OUTPUT / "phase82_seven_diagram_end_to_end_checkpoint.md"
    p83 = OUTPUT / "phase83_two_loop_completion_regression.md"
    require(p82)
    require(p83)

    lines = [
        "# QEDCalc complete two-loop calculation record — all seven diagrams",
        "",
        "This is the master process report for the validated two-loop electron "
        "anomalous-magnetic-moment calculation. The five graph-class reports below "
        "represent 1 + 1 + 2 + 2 + 1 = 7 Feynman diagrams.",
        "",
        "## 1. Report index", "",
        "| Diagram class | Multiplicity | Full report |",
        "| --- | ---: | --- |",
    ]
    for spec, path, _ in reports:
        lines.append(f"| {spec.title} | {spec.multiplicity} | `output/{path.name}` |")
    lines += ["", "## 2. Complete graph-class process records", ""]

    for n, (spec, path, content) in enumerate(reports, 1):
        lines += [
            f"### 2.{n} {spec.title}", "",
            f"Source report: `output/{path.name}`", "",
            demote_headings(content), "", "---", "",
        ]

    lines += [
        "## 3. Seven-diagram exact assembly", "",
        demote_headings(read(p82)), "", "---", "",
        "## 4. Complete two-loop regression", "",
        demote_headings(read(p83)), "",
        "## 5. Interpretation", "",
        "The graph-class sections contain the recorded calculation artifacts from "
        "raw input through each release checkpoint. Sections 3 and 4 then prove "
        "that the five graph classes represent seven diagrams, that the corner and "
        "self-energy IR logarithms cancel, and that the exact transcendental-basis "
        "sum reproduces the final two-loop coefficient.", "",
    ]
    out = OUTPUT / "2loop_all_7diagrams_full.md"
    out.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return out


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    reports = []
    for spec in SPECS:
        path, content = graph_report(spec)
        reports.append((spec, path, content))
        print("generated:", path.relative_to(ROOT))
    master = build_master(reports)
    print("generated:", master.relative_to(ROOT))
    print("Phase-84 full two-loop process reporting PASS")


if __name__ == "__main__":
    main()
