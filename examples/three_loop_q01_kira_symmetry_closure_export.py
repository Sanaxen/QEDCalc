"""Export symmetry-expansion integrals missing from the saved Q01 FireFly FORM graph.

No FireFly reduction or projected trace is recomputed.  The generator applies
Kira's saved momentum symmetries to the 60 projected-amplitude master forms,
expands numerator/ISP polynomials exactly, and collects every resulting Kira
integral that is absent from the already-exported wave-1 FORM graph.  Those
integrals are then requested from the existing FireFly database via kira2form.

The audit classifies each requested target as an exported reduction rule, zero,
Kira-reported master, or still unresolved.  It deliberately does not assume in
advance that the missing integrals are reducible rather than additional master
forms.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

import sympy as sp

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    ALT_DIR_NAME,
    ALT_ROOT,
    FAMILY,
    PROJECT,
    _find_export_files,
)
from examples.three_loop_q01_kira_momentum_map_isp_probe import (
    FILES,
    _build_p_basis_solution,
    _load_final_forms,
    _parse_mapping_line,
    _sector,
    _transformed_propagators,
)
from examples.three_loop_q01_kira_symmetry_linear_relation_probe import (
    _expand_transformed_integral,
    _loop_matrix,
)
from examples.three_loop_q01_projected_amplitude_firefly_reduce import (
    _load_weighted_form_graph,
)
from three_loop.kira_form_parser import iter_kira_form_rules

IndexTuple = tuple[int, ...]

TARGET_FILE = PROJECT / "q01_symmetry_closure_targets"
EXPORT_JOB = PROJECT / "jobs_q01_symmetry_closure_firefly_export.yaml"
EXPORT_LOG = PROJECT / "q01_symmetry_closure_firefly_export.log"
OUTPUT_JSON = PROJECT / "q01_symmetry_closure_firefly_export_audit.json"

_MASTER_RE = re.compile(
    rf"This requested integral is a master integral:\s*{re.escape(FAMILY)}\["
    r"(?P<args>-?\d+(?:\s*,\s*-?\d+){11})\]"
)
_TARGET_RE = re.compile(
    rf"^{re.escape(FAMILY)}\[(?P<args>-?\d+(?:\s*,\s*-?\d+){{11}})\]$"
)


def _integral_text(values: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in values)}]"


def _indices(text: str) -> IndexTuple:
    values = tuple(int(v.strip()) for v in text.split(","))
    if len(values) != 12:
        raise ValueError(f"expected 12 indices, got {len(values)}")
    return values


def _load_missing_targets() -> tuple[IndexTuple, ...]:
    forms = tuple(sorted(_load_final_forms()))
    basis_solution = _build_p_basis_solution()

    mappings_by_sector: dict[int, list[tuple[str, dict[str, dict[str, sp.Expr]], int]]] = {}
    for path in FILES:
        if not path.exists():
            raise SystemExit(f"ERROR: Kira sectormapping file not found: {path}")
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            item = _parse_mapping_line(line, source_file=path, line_no=line_no)
            if item is None:
                continue
            source_sector, _target_sector, momentum_map, _direct_map = item
            mappings_by_sector.setdefault(source_sector, []).append(
                (path.name, momentum_map, line_no)
            )

    form_file, masters_file = _find_export_files()
    rules, zero_rules, masters, terminal_rhs, _ = _load_weighted_form_graph(
        form_file, masters_file
    )
    known = set(rules) | set(zero_rules) | set(masters) | set(terminal_rhs)

    missing: set[IndexTuple] = set()
    applications = 0
    expanded_terms = 0
    for source in forms:
        for file_name, momentum_map, line_no in mappings_by_sector.get(_sector(source), []):
            det = sp.expand(_loop_matrix(momentum_map).det())
            if det not in (sp.Integer(1), sp.Integer(-1)):
                continue
            applications += 1
            images = _transformed_propagators(momentum_map, basis_solution)
            expanded = _expand_transformed_integral(source, images)
            if expanded is None:
                raise SystemExit(
                    f"ERROR: symmetry expansion unexpectedly failed for {_integral_text(source)} "
                    f"at {file_name}:{line_no}"
                )
            for _coefficient, target in expanded:
                expanded_terms += 1
                if target not in known:
                    missing.add(target)

    print("symmetry applications scanned:", applications)
    print("expanded integral terms scanned:", expanded_terms)
    print("unique integrals missing from saved FORM graph:", len(missing))
    return tuple(sorted(missing))


def generate() -> None:
    missing = _load_missing_targets()
    if not missing:
        raise SystemExit("ERROR: no missing symmetry-expansion integrals were found")

    TARGET_FILE.write_text(
        "\n".join(_integral_text(v) for v in missing) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    EXPORT_JOB.write_text(
        "jobs:\n"
        "  - kira2form:\n"
        "      target:\n"
        f"        - [{FAMILY},{TARGET_FILE.name}]\n"
        f"      alt_dir: {ALT_DIR_NAME}\n",
        encoding="utf-8",
        newline="\n",
    )

    print("generated target list:", TARGET_FILE)
    print("generated kira2form job:", EXPORT_JOB)
    print("Q01 symmetry-expansion closure export generation PASS")


def _load_targets() -> set[IndexTuple]:
    if not TARGET_FILE.exists():
        raise SystemExit(f"ERROR: target file not found: {TARGET_FILE}")
    out: set[IndexTuple] = set()
    for line_no, raw in enumerate(TARGET_FILE.read_text(encoding="utf-8").splitlines(), 1):
        text = raw.strip()
        if not text:
            continue
        match = _TARGET_RE.match(text)
        if not match:
            raise SystemExit(f"ERROR: malformed target line {line_no}: {text!r}")
        out.add(_indices(match.group("args")))
    return out


def _find_export_form() -> Path:
    result_dir = ALT_ROOT / "results" / FAMILY
    preferred = result_dir / "kira_q01_symmetry_closure_targets.inc"
    if preferred.is_file():
        return preferred
    candidates = sorted(
        (p for p in result_dir.glob("*.inc") if "symmetry_closure" in p.name),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]
    raise SystemExit(f"ERROR: symmetry-closure FORM export not found under {result_dir}")


def audit() -> None:
    targets = _load_targets()
    form_path = _find_export_form()

    rules: set[IndexTuple] = set()
    zeros: set[IndexTuple] = set()
    rhs_children: set[IndexTuple] = set()
    for rule in iter_kira_form_rules(form_path, family=FAMILY):
        lhs = tuple(int(v) for v in rule.lhs.indices)
        if rule.terms:
            rules.add(lhs)
            rhs_children.update(tuple(int(v) for v in term.integral.indices) for term in rule.terms)
        elif rule.is_zero:
            zeros.add(lhs)

    master_reports: set[IndexTuple] = set()
    log_text = ""
    if EXPORT_LOG.exists():
        log_text = EXPORT_LOG.read_text(encoding="utf-8", errors="strict")
        for match in _MASTER_RE.finditer(log_text):
            master_reports.add(_indices(match.group("args")))

    status = {
        "rule": len(targets & rules),
        "zero": len(targets & zeros),
        "kira_master": len(targets & master_reports),
        "still_no_rule_or_master_report": len(
            targets - rules - zeros - master_reports
        ),
    }
    unresolved = sorted(targets - rules - zeros - master_reports)

    # A rule may introduce further integrals not present in the original wave-1
    # graph.  Report them explicitly so a second closure export can be generated
    # if necessary without rerunning FireFly.
    wave1_form, masters_file = _find_export_files()
    base_rules, base_zeros, base_masters, base_terminal, _ = _load_weighted_form_graph(
        wave1_form, masters_file
    )
    known_after = (
        set(base_rules) | set(base_zeros) | set(base_masters) | set(base_terminal)
        | rules | zeros | master_reports
    )
    new_rhs_missing = sorted(v for v in rhs_children if v not in known_after)

    unreduced_zero = bool(re.search(r"unreduced integrals:\s*0\s*\.", log_text))
    summary = {
        "mode": "existing FireFly database; kira2form only; no reduction recomputation",
        "targets": len(targets),
        "form_export": str(form_path),
        "target_status": status,
        "kira_unreduced_integrals_zero": unreduced_zero,
        "unresolved_targets": [_integral_text(v) for v in unresolved],
        "new_rhs_integrals_missing_after_export": [
            _integral_text(v) for v in new_rhs_missing
        ],
        "pass": not unresolved and not new_rhs_missing and unreduced_zero,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print("QEDCalc Q01 symmetry-expansion closure export audit")
    print("requested unique missing integrals:", len(targets))
    print("exported reduction rules:", len(rules))
    print("exported zero rules:", len(zeros))
    print("Kira-reported masters:", len(master_reports))
    print("target status:", status)
    print("new RHS integrals still outside saved graph:", len(new_rhs_missing))
    print("Kira unreduced integrals = 0:", unreduced_zero)
    print("audit JSON:", OUTPUT_JSON)

    if unresolved:
        print("unresolved target samples:")
        for value in unresolved[:12]:
            print("  ", _integral_text(value))
    if new_rhs_missing:
        print("new RHS-missing samples:")
        for value in new_rhs_missing[:12]:
            print("  ", _integral_text(value))

    if not summary["pass"]:
        raise SystemExit(3 if (unresolved or new_rhs_missing) else 1)
    print("Q01 symmetry-expansion closure export audit PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("generate", "audit"))
    args = parser.parse_args()
    if args.mode == "generate":
        generate()
    else:
        audit()


if __name__ == "__main__":
    main()
