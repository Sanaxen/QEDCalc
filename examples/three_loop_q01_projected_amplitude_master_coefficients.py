"""Synthesize the saved Q01 projected amplitude exactly onto the finalized master basis.

This stage does not recompute the projected trace and does not run Kira.  It
combines three already validated ingredients:

* the saved 910-term native projected-amplitude artifact;
* the exact native-Q01 -> Kira ISP bridge;
* the completed r9s4d0 FireFly back-substituted reduction table.

The result is an exact symbolic coefficient for every finalized Q01 master.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path
import re
from typing import Iterable

import sympy as sp

from examples.three_loop_q01_saved_projected_amplitude_probe import (
    _INTEGRAL_RE,
    _extract_coefficient,
    _parse_coefficient,
)
from three_loop.kira_form_coefficients import form_coefficient_to_sympy
from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_isp_bridge import expand_qedcalc_integral_to_kira
from three_loop.kira_reducer import load_master_indices

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "output" / "3loop_q01_integral_indices.txt"
PROJECT = ROOT / "output" / "kira_q01_full_demand_r9s3d0"
FAMILY = "Q01_full"
ALT_ROOT = PROJECT / "exact944_r9s4d0_firefly"
RESULT_DIR = ALT_ROOT / "results" / FAMILY
TARGET_FILE = PROJECT / "q01_exact944_r9s4d0_firefly_boundary_targets"
ORIGINAL_TARGET_FILE = PROJECT / "q01_944_targets"
FINAL_BASIS_JSON = PROJECT / "q01_projected_amplitude_kira_master_basis.json"
OUTPUT_JSON = PROJECT / "q01_projected_amplitude_final60_coefficients.json"
OUTPUT_TXT = PROJECT / "q01_projected_amplitude_final60_coefficients.txt"

EXPECTED_NATIVE = 910
EXPECTED_ORIGINAL = 944
EXPECTED_FINAL = 60
IndexTuple = tuple[int, ...]


def _indices12(values: Iterable[int]) -> IndexTuple:
    out = tuple(int(v) for v in values)
    if len(out) != 12:
        raise ValueError(f"expected 12 indices, got {len(out)}")
    return out


def _fmt(v: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(x) for x in v)}]"


def _load_projected_terms() -> list[tuple[IndexTuple, sp.Expr, str]]:
    if not SOURCE.exists():
        raise SystemExit(f"ERROR: saved projected-amplitude artifact not found: {SOURCE}")
    records: list[tuple[IndexTuple, sp.Expr, str]] = []
    failures: list[str] = []
    for line_no, raw in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), 1):
        text = raw.strip()
        if not text:
            continue
        matches = list(_INTEGRAL_RE.finditer(text))
        if not matches:
            continue
        if len(matches) != 1:
            failures.append(f"line {line_no}: expected one I(...) token, got {len(matches)}")
            continue
        match = matches[0]
        try:
            indices = _indices12(int(v.strip()) for v in match.group(1).split(","))
            coefficient_text = _extract_coefficient(text, match)
            coefficient = _parse_coefficient(coefficient_text)
            # QEDCalc's projector historically uses D for the spacetime
            # dimension while Kira exports d.  They are the same variable.
            D = sp.Symbol("D")
            d = sp.Symbol("d")
            if D in coefficient.free_symbols:
                coefficient = coefficient.xreplace({D: d})
            records.append((indices, coefficient, coefficient_text))
        except Exception as exc:
            failures.append(f"line {line_no}: {exc}")
    if failures:
        raise SystemExit("ERROR: projected-amplitude parse failure(s):\n" + "\n".join(failures[:12]))
    if len(records) != EXPECTED_NATIVE:
        raise SystemExit(f"ERROR: expected {EXPECTED_NATIVE} projected terms, got {len(records)}")
    if len({r[0] for r in records}) != EXPECTED_NATIVE:
        raise SystemExit("ERROR: projected-amplitude artifact does not contain 910 unique native integrals")
    return records


def _load_family_file(path: Path, expected: int | None = None) -> set[IndexTuple]:
    if not path.exists():
        raise SystemExit(f"ERROR: target file not found: {path}")
    out: set[IndexTuple] = set()
    prefix = FAMILY + "["
    for raw in path.read_text(encoding="utf-8").splitlines():
        text = raw.strip()
        if not text:
            continue
        if not text.startswith(prefix) or not text.endswith("]"):
            raise SystemExit(f"ERROR: unexpected target syntax in {path.name}: {text!r}")
        out.add(_indices12(int(v.strip()) for v in text[len(prefix):-1].split(",")))
    if expected is not None and len(out) != expected:
        raise SystemExit(f"ERROR: {path.name} has {len(out)} unique targets; expected {expected}")
    return out


def _load_final60() -> set[IndexTuple]:
    if not FINAL_BASIS_JSON.exists():
        raise SystemExit(f"ERROR: final-basis JSON not found: {FINAL_BASIS_JSON}")
    data = json.loads(FINAL_BASIS_JSON.read_text(encoding="utf-8"))
    if not data.get("pass"):
        raise SystemExit("ERROR: final-basis JSON is not marked PASS")
    out: set[IndexTuple] = set()
    for row in data.get("basis_terms", []):
        raw = row.get("indices") if isinstance(row, dict) else None
        if isinstance(raw, list) and len(raw) == 12:
            out.add(_indices12(raw))
    if len(out) != EXPECTED_FINAL:
        raise SystemExit(f"ERROR: expected final60 basis, got {len(out)}")
    return out


def _find_form_export() -> Path:
    if not RESULT_DIR.exists():
        raise SystemExit(f"ERROR: r9s4d0 FireFly result directory not found: {RESULT_DIR}")
    preferred = RESULT_DIR / f"kira_{TARGET_FILE.name}.inc"
    candidates = [preferred]
    candidates.extend(sorted(RESULT_DIR.glob("*.inc"), key=lambda p: p.stat().st_mtime, reverse=True))
    form = next((p for p in candidates if p.is_file()), None)
    if form is None:
        raise SystemExit(f"ERROR: FORM export not found under {RESULT_DIR}")
    return form


def _load_reduction_graph(form_file: Path, masters_file: Path):
    masters = set(load_master_indices(masters_file, family=FAMILY))
    rules: dict[IndexTuple, tuple[tuple[sp.Expr, IndexTuple], ...]] = {}
    zeros: set[IndexTuple] = set()
    for rule in iter_kira_form_rules(form_file, family=FAMILY):
        lhs = _indices12(rule.lhs.indices)
        if lhs in rules or lhs in zeros:
            raise SystemExit(f"ERROR: duplicate FORM rule for {_fmt(lhs)}")
        if rule.terms:
            converted = tuple(
                (form_coefficient_to_sympy(term.coefficient_form), _indices12(term.integral.indices))
                for term in rule.terms
            )
            rules[lhs] = converted
        elif rule.is_zero:
            zeros.add(lhs)
        else:
            raise SystemExit(f"ERROR: non-integral/non-zero FORM rule for {_fmt(lhs)}")
    return masters, rules, zeros


def _make_resolver(masters, rules, zeros):
    memo: dict[IndexTuple, dict[IndexTuple, sp.Expr] | None] = {}
    active: set[IndexTuple] = set()
    missing: set[IndexTuple] = set()

    def resolve(key: IndexTuple) -> dict[IndexTuple, sp.Expr] | None:
        if key in memo:
            return memo[key]
        if key in masters:
            memo[key] = {key: sp.Integer(1)}
            return memo[key]
        if key in zeros:
            memo[key] = {}
            return memo[key]
        children = rules.get(key)
        if children is None:
            missing.add(key)
            memo[key] = None
            return None
        if key in active:
            raise SystemExit(f"ERROR: cycle detected while resolving {_fmt(key)}")
        active.add(key)
        parts: dict[IndexTuple, list[sp.Expr]] = defaultdict(list)
        for coeff, child in children:
            child_map = resolve(child)
            if child_map is None:
                active.remove(key)
                memo[key] = None
                return None
            for master, child_coeff in child_map.items():
                parts[master].append(coeff * child_coeff)
        active.remove(key)
        combined = {m: sp.Add(*vals) for m, vals in parts.items() if vals}
        memo[key] = combined
        return combined

    return resolve, missing


def _canonical(expr: sp.Expr) -> sp.Expr:
    if expr == 0:
        return sp.Integer(0)
    return sp.cancel(sp.together(expr))


def main() -> None:
    print("QEDCalc Q01 projected-amplitude -> final60 master coefficient synthesis")
    print("mode: saved projected amplitude + saved r9s4d0 FireFly reduction; no new Kira run")

    projected = _load_projected_terms()
    final60 = _load_final60()
    original944 = _load_family_file(ORIGINAL_TARGET_FILE, EXPECTED_ORIGINAL)
    mandatory971 = _load_family_file(TARGET_FILE)
    if not final60.issubset(mandatory971):
        raise SystemExit("ERROR: r9s4d0 mandatory target set does not contain final60")

    expanded_unique: set[IndexTuple] = set()
    expanded_total = 0
    bridge_records: list[tuple[sp.Expr, IndexTuple]] = []
    native_degrees: Counter[int] = Counter()
    source_symbols: set[str] = set()
    for native, projected_coeff, _ in projected:
        source_symbols.update(str(s) for s in projected_coeff.free_symbols)
        expansion = expand_qedcalc_integral_to_kira(native)
        native_degrees[expansion.native_isp_degree] += 1
        expanded_total += len(expansion.terms)
        for term in expansion.terms:
            expanded_unique.add(term.kira_indices)
            bridge_records.append((projected_coeff * term.coefficient, term.kira_indices))

    missing_from_exact944 = expanded_unique - original944
    extra_exact944 = original944 - expanded_unique
    if missing_from_exact944:
        raise SystemExit(
            f"ERROR: bridge produced {len(missing_from_exact944)} Kira targets outside saved exact944"
        )
    if extra_exact944:
        raise SystemExit(
            f"ERROR: saved exact944 contains {len(extra_exact944)} targets not produced by the 910 projected terms"
        )

    form_file = _find_form_export()
    masters_file = RESULT_DIR / "masters.final"
    if not masters_file.exists():
        raise SystemExit(f"ERROR: masters.final not found: {masters_file}")
    masters, rules, zeros = _load_reduction_graph(form_file, masters_file)
    resolve, missing = _make_resolver(masters, rules, zeros)

    master_parts: dict[IndexTuple, list[sp.Expr]] = defaultdict(list)
    reduced_bridge_terms = 0
    zero_bridge_terms = 0
    for amplitude_coeff, kira_indices in bridge_records:
        resolved = resolve(kira_indices)
        if resolved is None:
            continue
        if not resolved:
            zero_bridge_terms += 1
            continue
        reduced_bridge_terms += 1
        for master, reduction_coeff in resolved.items():
            master_parts[master].append(amplitude_coeff * reduction_coeff)

    if missing:
        print("unresolved Kira integrals:", len(missing))
        for value in sorted(missing)[:12]:
            print("  unresolved:", _fmt(value))
        raise SystemExit(3)

    raw_coefficients = {m: sp.Add(*parts) for m, parts in master_parts.items()}
    print("raw master forms before exact cancellation:", len(raw_coefficients))
    print("canonicalizing master coefficients...")
    canonical = {m: _canonical(expr) for m, expr in sorted(raw_coefficients.items())}
    nonzero = {m: expr for m, expr in canonical.items() if expr != 0}
    nonzero_final = {m: expr for m, expr in nonzero.items() if m in final60}
    nonzero_extra = {m: expr for m, expr in nonzero.items() if m not in final60}

    rows = []
    for master in sorted(final60):
        expr = canonical.get(master, sp.Integer(0))
        rows.append(
            {
                "indices": list(master),
                "integral": _fmt(master),
                "coefficient": str(expr),
                "nonzero": bool(expr != 0),
                "source_contributions": len(master_parts.get(master, [])),
                "symbols": sorted(str(s) for s in expr.free_symbols),
            }
        )

    pass_checks = {
        "projected_native_terms_910": len(projected) == EXPECTED_NATIVE,
        "bridge_unique_targets_match_exact944": expanded_unique == original944,
        "all_bridge_targets_resolved": not missing,
        "final_basis_has_60_forms": len(final60) == EXPECTED_FINAL,
        "final60_are_masters_in_r9s4d0": final60.issubset(masters),
        "no_nonzero_master_coefficients_outside_final60": not nonzero_extra,
    }
    passed = all(pass_checks.values())

    summary = {
        "mode": "exact saved-artifact coefficient synthesis; no projected trace or Kira recomputation",
        "source": str(SOURCE),
        "project": str(PROJECT),
        "reduction_alt_dir": str(ALT_ROOT),
        "form_export": str(form_file),
        "masters_file": str(masters_file),
        "projected_native_terms": len(projected),
        "projected_coefficient_symbols_after_D_to_d_normalization": sorted(source_symbols - {"D"} | ({"d"} if "D" in source_symbols else set())),
        "native_isp_degree_histogram": {str(k): v for k, v in sorted(native_degrees.items())},
        "bridge_expanded_terms_total": expanded_total,
        "bridge_unique_kira_targets": len(expanded_unique),
        "exact944_targets": len(original944),
        "mandatory_boundary_targets": len(mandatory971),
        "reduction_masters_final": len(masters),
        "reduction_rules": len(rules),
        "reduction_zero_rules": len(zeros),
        "reduced_bridge_terms": reduced_bridge_terms,
        "zero_bridge_terms": zero_bridge_terms,
        "raw_master_forms_before_cancellation": len(raw_coefficients),
        "nonzero_master_forms_after_cancellation": len(nonzero),
        "final60_forms": len(final60),
        "nonzero_final60_coefficients": len(nonzero_final),
        "nonzero_extra_master_coefficients": [
            {"indices": list(m), "coefficient": str(expr)}
            for m, expr in sorted(nonzero_extra.items())
        ],
        "basis_terms": rows,
        "checks": pass_checks,
        "pass": passed,
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 projected-amplitude -> final60 master coefficient synthesis",
        "",
        f"projected native terms: {len(projected)}",
        f"bridge expanded terms total: {expanded_total}",
        f"bridge unique Kira targets: {len(expanded_unique)}",
        f"exact944 targets: {len(original944)}",
        f"r9s4d0 masters.final forms: {len(masters)}",
        f"raw master forms before cancellation: {len(raw_coefficients)}",
        f"nonzero master forms after cancellation: {len(nonzero)}",
        f"final60 forms: {len(final60)}",
        f"nonzero final60 coefficients: {len(nonzero_final)}",
        f"nonzero extra master coefficients: {len(nonzero_extra)}",
        f"unresolved Kira integrals: {len(missing)}",
        "",
        "checks:",
    ]
    lines.extend(f"  {name}: {value}" for name, value in pass_checks.items())
    lines.append("")
    lines.append("final60 coefficients:")
    for row in rows:
        lines.append(f"  {row['integral']}  coefficient={row['coefficient']}")
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("projected native terms:", len(projected))
    print("bridge expanded terms total:", expanded_total)
    print("bridge unique Kira targets:", len(expanded_unique))
    print("r9s4d0 masters.final forms:", len(masters))
    print("nonzero master forms after cancellation:", len(nonzero))
    print("nonzero final60 coefficients:", len(nonzero_final))
    print("nonzero extra master coefficients:", len(nonzero_extra))
    print("unresolved Kira integrals:", len(missing))
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)
    if nonzero_extra:
        print("first nonzero extra masters:")
        for master, expr in list(sorted(nonzero_extra.items()))[:10]:
            print("  ", _fmt(master), "coefficient=", expr)
    if not passed:
        print("Q01 projected-amplitude final60 coefficient synthesis FAIL")
        raise SystemExit(1)
    print("Q01 projected-amplitude final60 coefficient synthesis PASS")


if __name__ == "__main__":
    main()
