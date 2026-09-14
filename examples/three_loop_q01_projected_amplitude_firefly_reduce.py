"""Reduce the saved Q01 projected amplitude through the completed FireFly/Kira table.

This stage deliberately reuses only saved artifacts:

* ``output/3loop_q01_integral_indices.txt`` for the 910 projected-amplitude
  coefficients and native QEDCalc integrals;
* the existing Q01 closure-wave-1 ``kira2form`` export under the FireFly
  ``alt_dir``.

Neither the expensive projected Dirac trace nor the FireFly reduction is
recomputed.  Native linear ISPs are first expanded into the Kira quadratic
basis.  The FORM reduction dependency graph is then recursively reduced to a
terminal basis consisting of explicit ``masters.final`` entries plus legitimate
terminal RHS leaves produced by Kira symmetry/canonicalization.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import time
from typing import Iterable

import sympy as sp

from examples.three_loop_q01_kira_910_exact_closure1_firefly_export_audit import (
    FAMILY,
    PROJECT,
    _find_export_files,
)
from examples.three_loop_q01_saved_projected_amplitude_probe import (
    EXPECTED_NATIVE,
    SOURCE,
    _INTEGRAL_RE,
    _extract_coefficient,
    _parse_coefficient,
)
from three_loop.kira_form_coefficients import form_coefficient_to_sympy
from three_loop.kira_form_parser import iter_kira_form_rules
from three_loop.kira_isp_bridge import expand_qedcalc_integral_to_kira
from three_loop.kira_reducer import load_master_indices


OUTPUT_JSON = PROJECT / "q01_projected_amplitude_firefly_reduced.json"
OUTPUT_TXT = PROJECT / "q01_projected_amplitude_firefly_reduced.txt"

IndexTuple = tuple[int, ...]
BasisVector = dict[IndexTuple, sp.Expr]


def _indices12(values: Iterable[int]) -> IndexTuple:
    result = tuple(int(v) for v in values)
    if len(result) != 12:
        raise ValueError(f"expected 12 integral indices, got {len(result)}")
    return result


def _integral_text(indices: IndexTuple) -> str:
    return f"{FAMILY}[{','.join(str(v) for v in indices)}]"


def _load_saved_projected_terms() -> tuple[tuple[sp.Expr, IndexTuple, str, int], ...]:
    if not SOURCE.exists():
        raise SystemExit(f"ERROR: saved Q01 projected-amplitude artifact not found: {SOURCE}")

    records: list[tuple[sp.Expr, IndexTuple, str, int]] = []
    seen: set[IndexTuple] = set()
    for line_no, raw in enumerate(SOURCE.read_text(encoding="utf-8").splitlines(), 1):
        text = raw.strip()
        if not text:
            continue
        matches = list(_INTEGRAL_RE.finditer(text))
        if not matches:
            # The canonical file may contain harmless header/comment lines.
            continue
        if len(matches) != 1:
            raise SystemExit(
                f"ERROR: saved projected-amplitude line {line_no} contains "
                f"{len(matches)} I(...) tokens; expected exactly one"
            )
        match = matches[0]
        indices = _indices12(int(v.strip()) for v in match.group(1).split(","))
        if indices in seen:
            raise SystemExit(f"ERROR: duplicate native integral on line {line_no}: {indices}")
        seen.add(indices)
        coefficient_text = _extract_coefficient(text, match)
        try:
            coefficient = _parse_coefficient(coefficient_text)
        except Exception as exc:
            raise SystemExit(
                f"ERROR: could not parse projected coefficient on line {line_no}: {exc}"
            ) from exc
        records.append((coefficient, indices, coefficient_text, line_no))

    if len(records) != EXPECTED_NATIVE or len(seen) != EXPECTED_NATIVE:
        raise SystemExit(
            "ERROR: saved projected-amplitude artifact is not the canonical 910-term set: "
            f"records={len(records)} unique={len(seen)} expected={EXPECTED_NATIVE}"
        )
    return tuple(records)


def _load_weighted_form_graph(
    form_file: Path,
    masters_file: Path,
) -> tuple[
    dict[IndexTuple, tuple[tuple[sp.Expr, IndexTuple], ...]],
    set[IndexTuple],
    set[IndexTuple],
    set[IndexTuple],
    Counter[str],
]:
    masters = set(load_master_indices(masters_file, family=FAMILY))
    rules: dict[IndexTuple, tuple[tuple[sp.Expr, IndexTuple], ...]] = {}
    zero_rules: set[IndexTuple] = set()
    symbol_counts: Counter[str] = Counter()

    for rule in iter_kira_form_rules(form_file, family=FAMILY):
        lhs = _indices12(rule.lhs.indices)
        if lhs in rules or lhs in zero_rules:
            raise SystemExit(f"ERROR: duplicate FORM reduction rule for {lhs}")
        if rule.terms:
            converted: list[tuple[sp.Expr, IndexTuple]] = []
            for term in rule.terms:
                rhs = _indices12(term.integral.indices)
                try:
                    coefficient = form_coefficient_to_sympy(term.coefficient_form)
                except Exception as exc:
                    raise SystemExit(
                        "ERROR: could not parse Kira FORM coefficient for "
                        f"{lhs} -> {rhs}: {term.coefficient_form!r}: {exc}"
                    ) from exc
                for symbol in coefficient.free_symbols:
                    symbol_counts[str(symbol)] += 1
                converted.append((coefficient, rhs))
            rules[lhs] = tuple(converted)
        elif rule.is_zero:
            zero_rules.add(lhs)
        else:
            raise SystemExit(
                "ERROR: FORM rule has neither integral RHS terms nor an explicit zero RHS: "
                f"{lhs} -> {rule.rhs_form!r}"
            )

    all_rhs = {rhs for terms in rules.values() for _, rhs in terms}
    terminal_rhs = {
        rhs
        for rhs in all_rhs
        if rhs not in masters and rhs not in zero_rules and rhs not in rules
    }
    return rules, zero_rules, masters, terminal_rhs, symbol_counts


def _accumulate(target: BasisVector, source: BasisVector, factor: sp.Expr) -> None:
    if factor == 0:
        return
    for basis, coefficient in source.items():
        term = factor * coefficient
        if term == 0:
            continue
        previous = target.get(basis)
        target[basis] = term if previous is None else previous + term


def _make_recursive_reducer(
    *,
    rules: dict[IndexTuple, tuple[tuple[sp.Expr, IndexTuple], ...]],
    zero_rules: set[IndexTuple],
    masters: set[IndexTuple],
    terminal_rhs: set[IndexTuple],
):
    memo: dict[IndexTuple, BasisVector] = {}
    active: list[IndexTuple] = []
    active_set: set[IndexTuple] = set()

    def reduce_one(key: IndexTuple) -> BasisVector:
        cached = memo.get(key)
        if cached is not None:
            return cached
        if key in masters or key in terminal_rhs:
            result = {key: sp.Integer(1)}
            memo[key] = result
            return result
        if key in zero_rules:
            result: BasisVector = {}
            memo[key] = result
            return result
        terms = rules.get(key)
        if terms is None:
            raise KeyError(f"Kira integral is not present in reduction graph: {key}")
        if key in active_set:
            start = active.index(key)
            cycle = active[start:] + [key]
            raise RuntimeError(f"cycle in Kira FORM dependency graph: {cycle}")

        active.append(key)
        active_set.add(key)
        result: BasisVector = {}
        try:
            for coefficient, child in terms:
                _accumulate(result, reduce_one(child), coefficient)
        finally:
            active.pop()
            active_set.remove(key)
        # Keep arithmetic exact but avoid expensive factor/simplify on every rule.
        result = {basis: coefficient for basis, coefficient in result.items() if coefficient != 0}
        memo[key] = result
        return result

    return reduce_one, memo


def _write_outputs(
    *,
    form_file: Path,
    masters_file: Path,
    projected_terms: tuple[tuple[sp.Expr, IndexTuple, str, int], ...],
    rules: dict[IndexTuple, tuple[tuple[sp.Expr, IndexTuple], ...]],
    zero_rules: set[IndexTuple],
    masters: set[IndexTuple],
    terminal_rhs: set[IndexTuple],
    kira_symbol_counts: Counter[str],
    final_vector: BasisVector,
    native_symbol_counts: Counter[str],
    expanded_total: int,
    unique_expanded: set[IndexTuple],
    memo_size: int,
    elapsed_seconds: float,
) -> None:
    nonzero = {basis: coefficient for basis, coefficient in final_vector.items() if coefficient != 0}
    used_explicit = sorted(set(nonzero) & masters)
    used_terminal = sorted(set(nonzero) & terminal_rhs)
    combined_symbols = sorted(
        {str(symbol) for coefficient in nonzero.values() for symbol in coefficient.free_symbols}
    )

    basis_rows = []
    for basis in sorted(nonzero):
        coefficient = nonzero[basis]
        basis_rows.append(
            {
                "kind": "master" if basis in masters else "terminal",
                "integral": _integral_text(basis),
                "indices": list(basis),
                "coefficient": str(coefficient),
                "symbols": sorted(str(symbol) for symbol in coefficient.free_symbols),
            }
        )

    summary = {
        "mode": "saved projected amplitude + saved FireFly FORM reduction; no trace/reduction recomputation",
        "projected_source": str(SOURCE),
        "form_export": str(form_file),
        "masters_file": str(masters_file),
        "native_projected_terms": len(projected_terms),
        "expanded_kira_terms_total": expanded_total,
        "unique_expanded_kira_integrals": len(unique_expanded),
        "form_reduction_rules": len(rules),
        "form_zero_rules": len(zero_rules),
        "explicit_kira_masters": len(masters),
        "terminal_rhs_leaves": len(terminal_rhs),
        "memoized_reduction_nodes": memo_size,
        "output_nonzero_basis_terms": len(nonzero),
        "output_explicit_master_terms": len(used_explicit),
        "output_terminal_terms": len(used_terminal),
        "native_coefficient_symbol_occurrences": dict(sorted(native_symbol_counts.items())),
        "kira_coefficient_symbol_occurrences": dict(sorted(kira_symbol_counts.items())),
        "final_free_symbols": combined_symbols,
        "elapsed_seconds": elapsed_seconds,
        "basis_terms": basis_rows,
        "pass": (
            len(projected_terms) == EXPECTED_NATIVE
            and len(unique_expanded) == 944
            and len(nonzero) > 0
            and len(nonzero) == len(used_explicit) + len(used_terminal)
        ),
    }
    OUTPUT_JSON.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "QEDCalc Q01 projected amplitude reduced through FireFly/Kira",
        "",
        f"native projected terms: {len(projected_terms)}",
        f"expanded Kira terms: {expanded_total}",
        f"unique expanded Kira integrals: {len(unique_expanded)}",
        f"explicit Kira masters available: {len(masters)}",
        f"terminal RHS leaves available: {len(terminal_rhs)}",
        f"nonzero output basis terms: {len(nonzero)}",
        f"elapsed seconds: {elapsed_seconds:.6f}",
        "",
        "Reduced projected amplitude:",
    ]
    for row in basis_rows:
        lines.append(f"[{row['kind']}] ({row['coefficient']}) * {row['integral']}")
    OUTPUT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("nonzero output basis terms:", len(nonzero))
    print("  explicit master terms:", len(used_explicit))
    print("  terminal terms:", len(used_terminal))
    print("final free symbols:", combined_symbols)
    print("memoized reduction nodes:", memo_size)
    print("elapsed seconds:", f"{elapsed_seconds:.3f}")
    print("output JSON:", OUTPUT_JSON)
    print("output TXT:", OUTPUT_TXT)
    for row in basis_rows[:8]:
        coefficient = row["coefficient"]
        preview = coefficient if len(coefficient) <= 180 else coefficient[:177] + "..."
        print(f"  [{row['kind']}] {row['integral']} coefficient={preview}")

    if not summary["pass"]:
        raise SystemExit("Q01 projected-amplitude FireFly reduction FAIL")


def main() -> None:
    started = time.perf_counter()
    print("QEDCalc Q01 saved projected-amplitude FireFly reduction")
    print("mode: saved artifacts only; projected trace and FireFly reduction are NOT recomputed")
    print("projected source:", SOURCE)

    projected_terms = _load_saved_projected_terms()
    native_symbol_counts: Counter[str] = Counter()
    for coefficient, _, _, _ in projected_terms:
        for symbol in coefficient.free_symbols:
            native_symbol_counts[str(symbol)] += 1
    print("native projected terms:", len(projected_terms))
    print("native coefficient symbols:", dict(sorted(native_symbol_counts.items())))

    form_file, masters_file = _find_export_files()
    print("FORM export:", form_file)
    print("master list:", masters_file)
    rules, zero_rules, masters, terminal_rhs, kira_symbol_counts = _load_weighted_form_graph(
        form_file, masters_file
    )
    print("FORM reduction rules:", len(rules))
    print("FORM zero rules:", len(zero_rules))
    print("explicit Kira masters:", len(masters))
    print("terminal RHS leaves:", len(terminal_rhs))
    print("Kira coefficient symbols:", dict(sorted(kira_symbol_counts.items())))

    reduce_one, memo = _make_recursive_reducer(
        rules=rules,
        zero_rules=zero_rules,
        masters=masters,
        terminal_rhs=terminal_rhs,
    )

    final_vector: BasisVector = {}
    unique_expanded: set[IndexTuple] = set()
    expanded_total = 0
    for item_no, (projected_coefficient, native, _, line_no) in enumerate(projected_terms, 1):
        try:
            expansion = expand_qedcalc_integral_to_kira(native)
        except Exception as exc:
            raise SystemExit(
                f"ERROR: native-to-Kira ISP expansion failed at saved line {line_no}: {native}: {exc}"
            ) from exc
        expanded_total += len(expansion.terms)
        for expanded in expansion.terms:
            unique_expanded.add(expanded.kira_indices)
            try:
                reduced = reduce_one(expanded.kira_indices)
            except Exception as exc:
                raise SystemExit(
                    "ERROR: FireFly FORM reduction failed for expanded Kira integral "
                    f"{expanded.kira_indices} from native {native}: {exc}"
                ) from exc
            _accumulate(
                final_vector,
                reduced,
                projected_coefficient * expanded.coefficient,
            )
        if item_no % 100 == 0 or item_no == len(projected_terms):
            print(
                f"  assembled native terms: {item_no}/{len(projected_terms)}; "
                f"memo nodes={len(memo)}; current basis terms={len(final_vector)}"
            )

    print("expanded Kira terms:", expanded_total)
    print("unique expanded Kira integrals:", len(unique_expanded))
    if len(unique_expanded) != 944:
        raise SystemExit(
            "ERROR: projected amplitude no longer expands to the validated exact944 set: "
            f"unique={len(unique_expanded)} expected=944"
        )

    elapsed = time.perf_counter() - started
    _write_outputs(
        form_file=form_file,
        masters_file=masters_file,
        projected_terms=projected_terms,
        rules=rules,
        zero_rules=zero_rules,
        masters=masters,
        terminal_rhs=terminal_rhs,
        kira_symbol_counts=kira_symbol_counts,
        final_vector=final_vector,
        native_symbol_counts=native_symbol_counts,
        expanded_total=expanded_total,
        unique_expanded=unique_expanded,
        memo_size=len(memo),
        elapsed_seconds=elapsed,
    )
    print("Q01 projected-amplitude FireFly reduction PASS")


if __name__ == "__main__":
    main()
